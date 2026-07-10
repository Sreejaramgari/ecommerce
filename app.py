from flask import Flask,request,jsonify,session,url_for,make_response
from werkzeug.middleware.proxy_fix import ProxyFix #AWS module
from datetime import timedelta
from flask_cors import CORS #for connecting backend with react becoz they run on different ports inorder to make compatibility communicate
from flask_session import Session
from flask_bcrypt import Bcrypt
from otp import genotp
from cmail import send_mail #email automation
from stoken import endata,dndata
from mysql.connector import (connection)
from werkzeug.utils import secure_filename
mydb=connection.MySQLConnection(user='root',host='localhost',password='root',database='ecomdbOnr12')
import re
import os #for file handling
import uuid
import razorpay #third party app
from io import BytesIO #it holds bytedata
from reportlab.platypus import (
    SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus.flowables import HRFlowable

BASE_DIR=os.path.abspath(os.path.dirname(__file__)) #file path
print(BASE_DIR)
UPLOAD_FOLDER=os.path.join(BASE_DIR,'static','uploads')#make files static and upload
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
ALLOWED_EXTENSION={"png","jpeg","gif","webp","jpg"}
MAX_CONTENT_LENGTH=6*1024*1024 #6MB

app=Flask(__name__)#api instance object
app.wsgi_app=ProxyFix(app.wsgi_app,x_proto=1,x_host=1)
app.config['PREFERRED_URL_SCHEME']='https'
app.permanent_session_lifetime=timedelta(days=1)
#enable react connection
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
bcrypt = Bcrypt(app)

#session validation
app.secret_key="Code2345"
app.config['SESSION_TYPE']='filesystem'
app.config['SESSION_COOKIE_SECURE']=True
app.config['SESSION_COOKIE_HTTPONLY']=True
app.config['SESSION_COOKIE_SAMESITE']="None"
Session(app)
client = razorpay.Client(auth=("rzp_test_TAKBSWibJCJdb6", "tFESfjyGUcyHZx8FxlyOyQG2")) #razorpay id and razoroay secret key from razorpay excel from app


#Home
@app.route('/',methods=['GET'])
def index():
    return jsonify({
        "status":"success",
        "Message":"Welcome to Flaskecom website"
    }),200
#admin register route
@app.route('/api/adminregister',methods=['POST'])
def adminregister():
    cursor=None
    try:
        data=request.get_json()#{dict form}
        if not data:
            return jsonify({
            "status":"failed",
            "Message":"No Input data given"
        }),400 
        admin_name=data.get('username','').strip()
        admin_email=data.get('useremail','').strip()
        admin_address=data.get('useraddress','').strip()
        admin_password=data.get('userpassword','').strip()
        admin_agree=data.get('useragree')
        if not admin_name:
            return jsonify({"status":"failed","message":"Username required"}),400
        email_pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern,admin_email):
            return jsonify({"status":"failed","message":"invalid Email"}),400
        if len(admin_password)<6:
            return jsonify({"status":"failed","message":"password too short"}),400
        hash_password=bcrypt.generate_password_hash(admin_password).decode('utf-8')
        print(hash_password)

        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from admindata where useremail=%s',[admin_email])
        email_count=cursor.fetchone()[0]#(0,)(1,)
        if email_count>0:
            return jsonify({'status':'failed','message':'Email Already existed'}),400

        gotp=genotp()
        admindata={
            'admin_username':admin_name,
            'admin_useremail':admin_email,
            'admin_address':admin_address,
            'admin_userpassword':hash_password,
            'admin_agree':admin_agree,
            'admin_otp':gotp
        }
        subject="Admin Registration Verification"
        body=f'Hello Admin,Your OTP is: {gotp} This OTP is valid for 5 mins.'
        send_mail(to=admin_email,subject=subject,body=body)
        token=endata(admindata)
        return jsonify({
            "status":"success",
            "Message":f"OTP has sent successfully",
            "token":token
        }),200
    except Exception as e:
        print('Error in Registration')
        return jsonify({
            "status":"failed",
            "Message":f"Could not sent otp{e}"
        }),500
    finally:
        if cursor:
            cursor.close()
#otp verify
@app.route('/api/admin/verify-otp',methods=['POST'])
def adminotpverify():
    cursor=None
    try:
        data=request.get_json()
        if not data:
            return jsonify({
            "status":"failed",
            "Message":"No Input given"
        }),400   
        userotp=data.get('otp')
        token=data.get('token')
        if not userotp or not token:
            return jsonify({
            "status":"failed",
            "Message":"otp and token required"
        }),400
        try:
            admin_details=dndata(token)
        except Exception as e:
            print(str(e))
            return jsonify({
            "status":"failed",
            "Message":"Invalid or Expired token"
        }),400
        #otp validation
        if str(userotp)!=str(admin_details['admin_otp']):
            return jsonify({
            "status":"failed",
            "Message":"Invalid otp"
        }),400
        #reconnect automatically if mysql connection lost
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from admindata where useremail=%s',[admin_details['admin_useremail']])
        email_exists=cursor.fetchone()[0]
        if email_exists>0:
            return jsonify({
                "status":"failed",
                "Message":"Email already registered"
            }),400
        cursor.execute('insert into admindata(adminid,username,useremail,password,agree,adminaddress) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s)',[admin_details['admin_username'],admin_details['admin_useremail'],admin_details['admin_userpassword'],admin_details['admin_agree'],admin_details['admin_address']])
        mydb.commit()
        return jsonify({
            "status":"success",
            "Message":"Admin registration successfull"
        }),200
    except Exception as e:
        mydb.rollback()
        print('Mysql error:',str(e))
        return jsonify({
            "status":"failed",
            "Message":"Could not verify"
        }),400   
    finally:
        if cursor:
            cursor.close()

#Login 
@app.route('/api/admin/login',methods=['POST'])
def adminlogin():
    cursor=None
    try:
        data=request.get_json()
        if not data:
            return jsonify({
            "status":"failed",
            "Message":"No Input given"
        }),400
        login_email=data.get('email','').strip()
        login_password=data.get('password','').strip()
        if not login_email or not login_password:
            return jsonify({
                "status":"failed",
                "Message":"Email and password required"
        }),400
        #my sql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(adminid),username,useremail,password from admindata where useremail=%s',[login_email])
        adminstored_data=cursor.fetchone()#(id,name,email,password)
        if not adminstored_data:
            return jsonify({
            "status":"failed",
            "Message":"Invalid Email"
            }),404
        adminid=adminstored_data[0]
        adminname=adminstored_data[1]
        adminemail=adminstored_data[2]
        stored_password=adminstored_data[3]

        if not bcrypt.check_password_hash(stored_password,login_password):
            return jsonify({
            "status":"failed",
            "Message":"Invalid Password"
        }),400
        session.permanent=True
        session['adminid']=adminid
        session['adminemail']=adminemail
        return jsonify({
            "status":"success",
            "Message":"Login Successful",
            'admin':{
                'adminid':adminid,
                'adminname':adminname,
                'adminemail':adminemail
            }
        }),200

    except Exception as e:
        print('Mysql Error:',str(e))
        return jsonify({
            "sattus":"failed",
            "Message":f"Could not verify login details{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#admin dashboard
@app.route('/api/admin/dashboard',methods=['GET'])
def admindashboard():
    try:
        if 'adminid' not in session:
            return jsonify({
                'status':'failed',
                'message':'Please login first'
            }),401
        return jsonify({
            'status':'success',
            'message':'Welcome to admin panel',
            'admin':{
                'adminid':session.get('adminid'),
                'adminemail':session.get('adminemail')
            }
        }),200
    except Exception as e:
        print(e)
        return jsonify({
            'status':'failed',
            'message':f'str(e)'
        }),500
def allowed_file(filename:str)->bool:
    return ("." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSION)
#add item in admin
@app.route('/api/admin/add-item',methods=['POST'])
def additem():
    try:
        if 'adminid' not in session:
            return jsonify({
                'status':'failed',
                'Message':'please login to add item'
            }),401
        item_name=request.form.get('title','').strip()
        item_description=request.form.get('Description','').strip()
        item_about=request.form.get('About_item','').strip()
        item_quantity=request.form.get('quantity','').strip()
        item_price=request.form.get('price','').strip()
        item_category=request.form.get('category','').strip()

        #form val;idation
        if not item_name:
            return jsonify({
                'status':'failed',
                'Message':'item name required'
            }),400
        try:
            item_price=float(item_price)
            item_quantity=int(item_quantity)
        except ValueError:
            return jsonify({
                'status':'failed',
                'Message':f'invalid price or quantity'
            }),400
        item_filedata=request.files.get('file')
        print(item_filedata)
        if not item_filedata:
            return jsonify({
                'status':'failed',
                'Message':f'Image required'
            }),400
        filename=item_filedata.filename
        if not item_filedata.mimetype.startswith("image/"):
            return jsonify({
                'status':'failed',
                'Message':f'Invalid Image'
            }),400
        if not allowed_file(filename):
            return jsonify({
                'status':'failed',
                'Message':f'Invalid file type'
            }),400
        safe_filename=secure_filename(filename) #it removes extra space,/,#
        ext=os.path.splitext(safe_filename)[1]
        filename=genotp()+ext #'K7iJ9m.jpg'
        save_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        item_filedata.save(save_path) #it save the file in static floder
        #mysql connection
        adminid=session.get('adminid')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('''insert into items(itemid,item_name,item_description,item_about,item_price,item_quantity,item_category,item_filename,added_by) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s,uuid_to_bin(%s))''',[item_name,item_description,item_about,item_price,item_quantity,item_category,filename,adminid])
        mydb.commit()
        return jsonify({
                'status':'success',
                'Message':f'Item added Successfully',
                'image':url_for('static',filename=f'uploads/{filename}',_external=True)
            }),200
    except Exception as e:
        mydb.rollback()
        print('Add item Error',str(e))
        #clean uploaded file
        if save_path and os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({
                'status':'failed',
                'message':f'{str(e)}'
            }),500


#view all items 
@app.route('/api/admin/items',methods=['GET'])
def viewallitems():
    cursor=None
    try:
        #session validation
        if 'adminid' not in session:
            return jsonify({
                'status':'failed',
                'message':f'pls Login to view all items'
            }),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        adminid=session.get('adminid')
        cursor.execute('''select bin_to_uuid(itemid),item_name,item_description,item_about,item_price,item_quantity,item_category,item_filename from items where added_by=uuid_to_bin(%s)''',[adminid])
        allitems_data=cursor.fetchall() #[(item1,),(item2)]
        products=[]
        for item in allitems_data:
            products.append({
                'itemid':item[0],
                'itemname':item[1],
                'item_desc':item[2],
                'item_about':item[3],
                'price':float(item[4]),
                'quantity':item[5],
                'category':item[6],
                'image':url_for('static',filename=f'uploads/{item[7]}',_external=True)
            })
        return jsonify({
                'status':'success',
                'message':f'All Items data',
                'products':products
            }),200
    except Exception as e:
         print('VIEW ITEMS ERROR:',str(e))
         return jsonify({
                'status':'failed',
                'message':f'{str(e)}'
            }),500
    finally:
        if cursor:
            cursor.close()

#view single item
@app.route('/api/admin/item/<itemid>',methods=['GET'])
def viewitem(itemid):
    cursor=None
    try:
        #session validation
        if 'adminid' not in session:
            return jsonify({
                'status':'failed',
                'message':f'pls Login to view all items'
            }),400
        try:
            uuid.UUID(itemid)
        except ValueError:
            return jsonify({
                'status':'failed',
                'message':f'Invalid Item id'
            }),400
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        adminid=session.get('adminid')
        cursor.execute('''select bin_to_uuid(itemid),item_name,item_description,item_about,item_price,item_quantity,item_category,item_filename from items where added_by=uuid_to_bin(%s) and itemid=uuid_to_bin(%s)''',[adminid,itemid])
        item_data=cursor.fetchone() #[(item1,),(item2)]
        product={
                'itemid':item_data[0],
                'itemname':item_data[1],
                'item_desc':item_data[2],
                'item_about':item_data[3],
                'price':float(item_data[4]),
                'quantity':item_data[5],
                'category':item_data[6],
                'image':url_for('static',filename=f'uploads/{item_data[7]}',_external=True)
            }
        return jsonify({
                'status':'success',
                'message':f'All Items data',
                'product':product
            }),200
    except Exception as e:
         print('VIEW ITEM ERROR:',str(e))
         return jsonify({
                'status':'failed',
                'message':f'{str(e)}'
            }),500
    finally:
        if cursor:
            cursor.close()

#delete item
@app.route('/api/admin/delete-item/<itemid>',methods=['DELETE'])
def deleteitem(itemid):
    cursor=None
    try:
        #session validation
        if 'adminid' not in session:
            return jsonify({
                'status':'failed',
                'message':'Pls login first'
            }),401
        #validate uuid
        try:
            uuid.UUID(itemid)
        except ValueError:
            return jsonify({
                'status':'failed',
                'message':'Invalid item ID'
            }),404
        adminid=session.get('adminid')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select item_filename from items where itemid=uuid_to_bin(%s) and added_by=uuid_to_bin(%s)',[itemid,adminid])
        item_data=cursor.fetchone()
        if not item_data:
            return  jsonify({
                'status':'failed',
                'message':'Item not found in DB'
            }),404
        image_name=item_data[0]
        remove_path=os.path.join(app.config['UPLOAD_FOLDER'],image_name)
        #delete database first
        cursor.execute('delete from items where itemid=uuid_to_bin(%s) and added_by=uuid_to_bin(%s)',[itemid,adminid])
        mydb.commit()
        #delete image data static folder
        if os.path.exists(remove_path):
            os.remove(remove_path)
        return jsonify({
            'status':"success",
            "message":"Item Deleted successfully"
        }),200
    except Exception as e:
        mydb.rollback()
        print('DELETE ITEM ERROR:',str(e))
        return jsonify({
            'status':'failed',
            'message':f'{str(e)}'
        }),500
    finally:
        if cursor:
            cursor.close()

#Update item() only price data
@app.route('/api/admin/update-item/<itemid>',methods=['PUT'])
def updateitem(itemid):
    new_image_path=None
    old_image_path=None
    cursor=None
    try:
        #session validation
        if 'adminid' not in session:
            return jsonify({
                "status":'failed',
                "message":"Pls login first"
            }),400
        try:
            uuid.UUID(itemid)
        except ValueError:
            return jsonify({
                "status":'failed',
                "message":"Inavlid item id"
            }),400
        #receive form data
        updateditem_name=request.form.get('title','').strip()
        updateditem_description=request.form.get('Description','').strip()
        updateditem_about=request.form.get('About_item','').strip()
        updateditem_quantity=request.form.get('quantity','').strip()
        updateditem_price=request.form.get('price','').strip()
        updateditem_category=request.form.get('category','').strip()
        #validations
        if not updateditem_name:
            return jsonify({
                "status":'failed',
                "message":"Item name required"
            }),400
        try:
            updateditem_price=float(updateditem_price)
            updateditem_quantity=int(updateditem_quantity)
        except ValueError:
            return jsonify({
                "status":'failed',
                "message":"Inavlid price or quantity"
            }),400
        #database connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        adminid=session.get('adminid')
        cursor.execute('select item_filename from items where added_by=uuid_to_bin(%s) and itemid=uuid_to_bin(%s)',[adminid,itemid])
        item_data=cursor.fetchone()
        if not item_data:
            return jsonify({
                'status':'failed',
                'message':'Item not found'
            }),404
        old_image=item_data[0]
        filename=old_image
        updateditem_filedata=request.files.get('file') #new image
        print(request.form)
        print(updateditem_filedata)
        if updateditem_filedata:
            uploaded_filename=updateditem_filedata.filename
            
            if not updateditem_filedata.mimetype.startswith('application/octet-stream'):
                return jsonify({
                    'status':'failed',
                    'message':f'Invalid image'
                }),400
            if not allowed_file(uploaded_filename):
                return  jsonify({
                    'status':'failed',
                    'message':f'Invalid file type'
                }),400
            safe_filename=secure_filename(uploaded_filename) #it remove extra space,/,#
            ext=os.path.splitext(safe_filename)[1]
            filename=genotp()+ext #'K7iJ9m.jpg'
            new_image_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            updateditem_filedata.save(new_image_path)
            #old imagepath
            old_image_path=os.path.join(app.config['UPLOAD_FOLDER'],old_image)
        #update item details in database 
        cursor.execute('update items set item_name=%s,item_description=%s,item_about=%s,item_price=%s,item_quantity=%s,item_category=%s,item_filename=%s where added_by=uuid_to_bin(%s) and itemid=uuid_to_bin(%s)',[updateditem_name,updateditem_description,updateditem_about,updateditem_price,updateditem_quantity,updateditem_category,filename,adminid,itemid])  
        mydb.commit()
        cursor.close()
        if (updateditem_filedata and old_image_path and os.path.exists(old_image_path)):
            os.remove(old_image_path)
        return jsonify({
                "status":'success',
                "message":"Item Updated successfully",
                'image':url_for('static',filename=f'uploads/{filename}',_external=True)
            }),200
    except Exception as e:
        mydb.rollback()
        #remove newly uploaded image if db fails
        if (new_image_path and os.path.exists(new_image_path)):
            os.remove(new_image_path)
        return jsonify({
                "status":'failed',
                "message":f"{str(e)}"
            }),500
    finally:
        if cursor:
            cursor.close()

# admin profile update
@app.route('/api/admin/profile-update',methods=['PUT'])
def adminprofileupdate():
    new_image_path=None
    old_image_path=None
    try:
        if 'adminid' not in session:
            return jsonify({
                "status":"failed",
                "message":"pls login first"
            }),401
        #receive form data
        updated_adminname=request.form.get('adminname','').strip()
        updated_adminaddress=request.form.get('address','').strip()
        updated_adminphone=request.form.get('ph_no','').strip()
        #validations
        if not updated_adminname:
            return  jsonify({
                "status":"failed",
                "message":"admin name required"
            }),401
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        adminid=session.get('adminid')
        cursor.execute('select adminid,username,admin_phone,adminaddress,filename from admindata where adminid=uuid_to_bin(%s)',[adminid])
        admin_data=cursor.fetchone()
        if not admin_data:
            return jsonify({
                "status":"failed",
                "message":"Admin not found"
            }),404
        old_image=admin_data[4]
        filename=old_image
        updated_adminprofile=request.files.get('file')
        if updated_adminprofile:
            uploaded_filename=updated_adminprofile.filename
            if not updated_adminprofile.mimetype.startswith('application/octet-stream'):
                return jsonify({
                    'status':'failed',
                    'message':f'Invalid image'
                }),400
            if not allowed_file(uploaded_filename):
                return  jsonify({
                    'status':'failed',
                    'message':f'Invalid file type'
                }),400
            safe_filename=secure_filename(uploaded_filename) #it remove extra space,/,#
            ext=os.path.splitext(safe_filename)[1]
            filename=genotp()+ext #'K7iJ9m.jpg'
            new_image_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            updated_adminprofile.save(new_image_path)
            #old imagepath
            if old_image:
                old_image_path=os.path.join(app.config['UPLOAD_FOLDER'],old_image)
        #db connection data store
        cursor.execute('''update admindata set username=%s,adminaddress=%s,admin_phone=%s,filename=%s where adminid=uuid_to_bin(%s)''',[updated_adminname,updated_adminaddress,updated_adminphone,filename,adminid])   
        mydb.commit()
        cursor.close()
        #delete old image data after db success
        if (updated_adminprofile and old_image_path and os.path.exists(old_image_path)):
            os.remove(old_image_path)
        return jsonify({
            'status':'success',
            'message':"Admin Profile Updated successfully",
            'profile_image':url_for('static',filename=f'uploads/{filename}',_external=True)
        }),200
    except Exception as e:
        mydb.rollback()
        print('PROFILE UPdATE ERROR',str(e))
        #remove newly uploaded image if db fails
        if (new_image_path and os.path.exists(new_image_path)):
            os.remove(new_image_path)
        return jsonify({
                "status":'failed',
                "message":f"{str(e)}"
            }),500
    finally:
        if cursor:
            cursor.close()

#admin logout
@app.route('/api/admin/logout',methods=['POST'])
def adminlogout():
    try:
        #check session
        if 'adminid' not in session:
            return jsonify({
                "status":'failed',
                "message":"please login first"
            }),401
        #clear complete session
        session.clear()
        return jsonify({
                "status":'success',
                "message":"Logout Successfull"
            }),200
    except Exception as e:
        return jsonify({
                "status":'failed',
                "message":f"{str(e)}"
            }),500
    
#user register route
@app.route('/api/user/register',methods=['POST'])
def usercreate():
    cursor=None
    try:
        data=request.get_json()#{dict form}
        if not data:
            return jsonify({
            "status":"failed",
            "Message":"No Input data given"
        }),400 
        user_name=data.get('username','').strip()
        user_email=data.get('useremail','').strip()
        user_address=data.get('useraddress','').strip()
        user_password=data.get('userpassword','').strip()
        user_gender=data.get('usergender')
        user_phone=data.get('userphone','').strip()
        if not user_name:
            return jsonify({"status":"failed","message":"Username required"}),400
        email_pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$' #email verification
        if not re.match(email_pattern,user_email):
            return jsonify({"status":"failed","message":"invalid Email"}),400
        if len(user_password)<6:
            return jsonify({"status":"failed","message":"password too short"}),400
        hash_password=bcrypt.generate_password_hash(user_password).decode('utf-8')
        print(hash_password)

        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from userdata where useremail=%s',[user_email])
        email_count=cursor.fetchone()[0]#(0,)(1,)
        if email_count>0:
            return jsonify({'status':'failed','message':'Email Already existed'}),400

        gotp=genotp()
        userdata={
            'user_username':user_name,
            'user_useremail':user_email,
            'user_address':user_address,
            'user_userpassword':hash_password,
            'user_gender':user_gender,
            'user_phone':user_phone,
            'user_otp':gotp
        }
        subject="Admin Registration Verification"
        body=f'Hello User,Your OTP is: {gotp} This OTP is valid for 5 mins.'
        send_mail(to=user_email,subject=subject,body=body)
        token=endata(userdata)
        return jsonify({
            "status":"success",
            "Message":f"OTP has sent successfully",
            "token":token
        }),200
    except Exception as e:
        print('Error in Registration')
        return jsonify({
            "status":"failed",
            "Message":f"Could not sent otp{e}"
        }),500
    finally:
        if cursor:
            cursor.close()

# User Otp verify
@app.route('/api/user/verify-otp',methods=['POST'])
def userotpverify():
    cursor=None
    try:
        data=request.get_json()
        if not data:
            return jsonify({
            "status":"failed",
            "Message":"No Input given"
        }),400
        userotp=data.get('otp')
        token=data.get('token')
        if not userotp or not token:
            return jsonify({
            "status":"failed",
            "Message":"otp and token required"
        }),400
        try:
            user_details=dndata(token)
        except Exception as e:
            print(str(e))
            return jsonify({
            "status":"failed",
            "Message":"Invalid or expired token"
        }),400
        #otp validation
        if str(userotp)!=str(user_details['user_otp']):
            return jsonify({
            "status":"failed",
            "Message":"Invalid otp"
        }),400
        #reconnect automatically if mysql connection lost
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from userdata where useremail=%s',[user_details['user_useremail']])
        email_exists=cursor.fetchone()[0]
        if email_exists>0:
            return jsonify({
            "status":"failed",
            "Message":"Email already registered"
        }),400
        cursor.execute('insert into userdata(userid,username,useremail,userpassword,usergender,useraddress,userphone) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s)',[user_details['user_username'],user_details['user_useremail'],user_details['user_userpassword'],user_details['user_gender'],user_details['user_address'],user_details['user_phone']])
        mydb.commit()
        return jsonify({
            "status":"success",
            "Message":"User registration successful"
        }),200
    except Exception as e:
        mydb.rollback()
        print('mysql error :',str(e))
        return jsonify({
            "status":"failed",
            "Message":"Could not verify OTp"
        }),400 
    finally:
        if cursor:
            cursor.close()

#User Login
@app.route('/api/user/login',methods=['POST'])
def userlogin():
    cursor=None
    try:
        data=request.get_json()
        if not data:
            return jsonify({
            "status":"failed",
            "Message":"No Input given"
        }),400
        login_email=data.get('email','').strip()
        login_password=data.get('password','').strip()
        if not login_email or not login_password:
            return jsonify({
            "status":"failed",
            "Message":"Email and password required"
        }),400 
        #my sql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(userid),username,useremail,userpassword from userdata where useremail=%s',[login_email])
        userstored_data=cursor.fetchone()#(id,name,email,password)
        if not userstored_data:
            return jsonify({
            "status":"failed",
            "Message":"Invalid Email"
        }),404
        userid=userstored_data[0]
        username=userstored_data[1]
        useremail=userstored_data[2]
        stored_password=userstored_data[3]
        
        if not bcrypt.check_password_hash(stored_password,login_password):
            return jsonify({
            "status":"failed",
            "Message":"Invalid password"
        }),400
        session.permanent=True
        session['userid']=userid
        session['useremail']=useremail
        return jsonify({
            "status":"success",
            "message":"Login successfull",
            'user':{
                'userid':userid,
                'username':username,
                'useremail':useremail
            }
        }),200
    except Exception as e:
        print('Mysql Error:',str(e))
        return jsonify({
            "status":"failed",
            "Message":f"Could not verify login details{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#Product Listing
@app.route('/api/products',methods=['GET'])
def home():
    cursor=None
    try:
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        adminid=session.get('adminid')
        cursor.execute('''select bin_to_uuid(itemid),item_name,item_description,item_about,item_price,item_quantity,item_category,item_filename from items''')
        allitems_data=cursor.fetchall() #[(item1,),(item2)]
        products=[]
        for item in allitems_data:
            products.append({
                'itemid':item[0],
                'itemname':item[1],
                'item_desc':item[2],
                'item_about':item[3],
                'price':float(item[4]),
                'quantity':item[5],
                'category':item[6],
                'image':url_for('static',filename=f'uploads/{item[7]}',_external=True)
            })
        return jsonify({
                'status':'success',
                'message':f'All Items data',
                'products':products
            }),200
    except Exception as e:
         print('VIEW ITEMS ERROR:',str(e))
         return jsonify({
                'status':'failed',
                'message':f'{str(e)}'
            }),500
    finally:
        if cursor:
            cursor.close()

#Add cart
@app.route('/api/cart/add',methods=['POST'])
def addcart():
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                "status":"failed",
                "message":"Please login first"
            }),401
        data=request.get_json()
        if not data:
            return jsonify({
                "status":"failed",
                "message":"No input data given"
            }),401
        itemid=data.get('itemid')
        quantity=int(data.get('quantity',1))
        if not itemid:
            return jsonify({
                "status":"failed",
                "message":"Item id Required"
            }),400
        #mysqlconnection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        #check itemid in items table
        cursor.execute('select item_quantity from items where itemid=uuid_to_bin(%s)',[itemid])
        stock=cursor.fetchone()
        if not stock:
            return jsonify({
                "status":"failed",
                "message":"No item found"
            }),400
        #quantity check
        if quantity > stock[0]:
            return jsonify({
                "status":"failed",
                "message":"Insufficient Quantity"
            }),400
        #already in cart
        cursor.execute('select quantity from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[itemid,userid])
        existing_cart=cursor.fetchone()
        #update quantity
        if existing_cart:
           new_quantity=existing_cart[0]+quantity
           if new_quantity>stock[0]:
               return jsonify({
                "status":"failed",
                "message":"Insufficient stock"
            }),400
           cursor.execute('update cart set quantity=%s where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[new_quantity,itemid,userid])
           message='Cart quantity updated'
        else:
            cursor.execute('insert into cart(cartid,itemid,userid,quantity) values(uuid_to_bin(uuid()),uuid_to_bin(%s),uuid_to_bin(%s),%s)',[itemid,userid,quantity])
            message='Item added to cart'
        mydb.commit()
        return jsonify({
                "status":"success",
                "message":message
            }),200
    except Exception as e:
        mydb.rollback()
        print('Mysql error',str(e))
        return jsonify({
                "status":"failed",
                "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

    
#user logout
@app.route('/api/user/logout',methods=['POST'])
def userlogout():
    try:
        #check session
        if 'userid' not in session:
            return jsonify({
                "status":'failed',
                "message":"please login first"
            }),401
        #clear complete session
        session.clear()
        return jsonify({
                "status":'success',
                "message":"Logout Successfull"
            }),200
    except Exception as e:
        return jsonify({
                "status":'failed',
                "message":f"{str(e)}"
            }),500

#view cart (My cart)
@app.route('/api/cart/view',methods=['GET'])
def viewcart():
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                "status":'failed',
                "message":"please login first"
            }),401
        #mydb connection
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        cursor.execute('select bin_to_uuid(i.itemid),i.item_name,i.item_price,c.quantity,i.item_category,i.item_filename from cart c join items i on c.itemid=i.itemid where c.userid=uuid_to_bin(%s)',[userid])
        cart_items=cursor.fetchall()
        if not cart_items:
            return jsonify({
                "status":'failed',
                "message":"CART IS EMPTY"
            }),404
        subtotal=0
        items_data=[]
        for item in cart_items:
            itemid=item[0]
            item_name=item[1]
            item_price=float(item[2])
            item_quantity=int(item[3])
            item_category=item[4]
            item_imgname=item[5]
            total=item_price*item_quantity
            subtotal += total
            image_url=url_for('static',filename=f'uploads/{item_imgname}',_external=True)
            items_data.append({
                'itemid':itemid,
                'itemname':item_name,
                'price':item_price,
                'quantity':item_quantity,
                'category':item_category,
                'image':image_url,
                'total':total
            })
        delivery=40
        tax=round(subtotal*0.05,2)
        grand_total=subtotal+tax+delivery
        return jsonify({
                "status":'success',
                "cart_items":items_data,
                "summary":{
                    "subtotal":subtotal,
                    "delivery":delivery,
                    "tax":tax,
                    "grand_total":grand_total
                }
            }),200
    except Exception as e:
        print("MYSQL Error:",str(e))
        return jsonify({
                "status":'failed',
                "message":f"{str(e)}"
            }),500
    finally:
        if cursor:
            cursor.close()

#update Cart item(Quantity update)
@app.route('/api/cart/update',methods=['PUT'])
def updatecart():
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                'status':"failed",
                "message":"pls login first"
            }),401
        data=request.get_json()
        if not data:
            return jsonify(
                {
                    "status":"failed",
                    "message":"No input data given"
                }
            ),401
        itemid=data.get('itemid')
        updated_quantity=int(data.get('quantity',0))
        if not itemid:
            return jsonify({
                "status":"failed",
                "message":"Item is required"
            }),400
        if updated_quantity<=0:
            return jsonify({
                "status":"failed",
                "message":"quantity must be greater than 0"
            }),400
        #mysql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        #check itemid in items table
        cursor.execute('select item_quantity from items where itemid=uuid_to_bin(%s)',[itemid])
        stock=cursor.fetchone()
        if not stock:
            return jsonify({
                "status":"failed",
                "message":"No item found"
            }),400
        #quantity check
        if updated_quantity > stock[0]:
            return jsonify({
                "status":"failed",
                "message":"Insufficient stock"
            }),400
        #already in cart?
        cursor.execute('select quantity from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[itemid,userid])
        existing_cart=cursor.fetchone()
        if not existing_cart:
            return jsonify({
                "status":"failed",
                "message":"Item not in cart"
            })
        # if existing_cart:
        #     new_quantity=existing_cart[0]+updated_quantity
        #     if new_quantity>stock[0]:
        #         return jsonify({
        #         "status":"failed",
        #         "message":"Insufficient stock"
        #     }),400
        cursor.execute('update cart set quantity=%s where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[updated_quantity,itemid,userid])
        mydb.commit()
        return jsonify({
            "status":'success',
            "message":'Cart updated successfully'
        })
    except Exception as e:
        mydb.rollback()
        print('Mysql error ',str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#delete item from cart
@app.route('/api/cart/remove/<itemid>',methods=['DELETE']) 
def removecart(itemid):
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                'status':"failed",
                "message":"pls login first"
            }),401
        #mysql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        #already in cart?
        cursor.execute('select quantity from cart where itemid=uuid_to_bin(%s) and userid=uuid_to_bin(%s)',[itemid,userid])
        existing_cart=cursor.fetchone()
        if not existing_cart:
            return jsonify({
                "status":"failed",
                "message":"Item not in cart"
            })
        #remove cart item
        cursor.execute('DELETE from cart where userid=uuid_to_bin(%s) and itemid=uuid_to_bin(%s)',[userid,itemid])
        mydb.commit()
        return jsonify({
            "status":"success",
            "message":'item removed from cart'
        }),200
    except Exception as e:
        mydb.rollback()
        print('Mysql error ',str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#razor pay
@app.route('/api/payment/create-order',methods=['POST'])
def pay_cart():
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                'status':"failed",
                "message":"pls login first"
            }),401
        data=request.get_json()
        payment_type=data.get('type','cart')
        #mysql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        #cart payment
        if payment_type=='cart':
            cursor.execute('select bin_to_uuid(i.itemid),i.item_name,i.item_price,c.quantity,i.item_category,i.item_filename from cart c join items i on c.itemid=i.itemid where c.userid=uuid_to_bin(%s)',[userid])
            cart_items=cursor.fetchall()
        else:
            itemid=data.get('itemid')
            quantity=int(data.get('quantity',1))
            cursor.execute('select bin_to_uuid(i.itemid),i.item_name,i.item_price,i.quantity,i.item_category,i.item_filename from items i where i.itemid=uuid_to_bin(%s)',[itemid])
            item=cursor.fetchone()
            if not item:
                return jsonify({
                'status':"failed",
                "message":"No item found"
            }),404
            available_stock=item[3]
            if quantity>available_stock:
                return jsonify({
                    'status':"failed",
                    "message":"Insufficient stock"
            })
            cart_items=[(item[0],item[1],item[2],quantity,item[4],item[5])]
        if not cart_items:
            return jsonify({
                'status':"failed",
                "message":"cart is empty"
            })
        subtotal=0
        items_data=[]
        for item in cart_items:
            itemid=item[0]
            item_name=item[1]
            item_price=float(item[2])
            item_quantity=int(item[3])
            item_category=item[4]
            item_imgname=item[5]
            total=item_price*item_quantity
            subtotal += total
            image_url=url_for('static',filename=f'uploads/{item_imgname}',_external=True)
            items_data.append({
                'itemid':itemid,
                'itemname':item_name,
                'price':item_price,
                'quantity':item_quantity,
                'category':item_category,
                'image':image_url,
                'total':total
            })
        delivery=40
        tax=round(subtotal*0.05,2)
        grand_total=subtotal+tax+delivery
        #razorpay payment
        razorpay_amount=int(grand_total*100)
        order=client.order.create({
            "amount":razorpay_amount,
            "currency":"INR",
            "receipt":str(userid),
            "payment_capture":1
        })
        return jsonify({
                'status':"success",
                'order':{
                    'order_id':order['id'],
                    'amount':order['amount'],
                    'currency':order['currency']
                },
                'cart_items':items_data,
                "summary":{
                    "subtotal":subtotal,
                    "delivery":delivery,
                    "tax":tax,
                    "grand_total":grand_total
                },
                'razorpay_key':'rzp_test_TAKBSWibJCJdb6'
            })
    except Exception as e:
        mydb.rollback()
        print('Mysql error ',str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#payment verify
@app.route('/api/payment/verify',methods=['POST'])
def verify_payment():
    cursor=None
    try:
        data=request.get_json()
        #---------------get frontend data ------------
        if not data:
            return jsonify({
                "status":"failed",
                "message":"Payment unsuccessfull"
            })
        payment_id=data.get('razorpay_payment_id')
        order_id=data.get('razorpay_order_id')
        signature=data.get('razorpay_signature')
        mode=data.get('mode','cart')
        #verifying payment signature
        params_dict={
            "razorpay_order_id":order_id,
            "razorpay_payment_id":payment_id,
            "razorpay_signature":signature
        }
        try:
            client.utility.verify_payment_signature(params_dict)
        except Exception as e:
            print(e)
            return jsonify({
                "status":"failed",
                "message":"Payment verification failed"
            }),400
        #---- LOGIN validation
        if 'userid' not in session:
            return jsonify({
                "status":"failed",
                "message":"pls login first"
            }),401
        #mysql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        #-------------Get cart items
        if mode=='cart':
            cursor.execute('select bin_to_uuid(i.itemid),i.item_name,i.item_price,c.quantity,i.item_category,i.item_filename from cart c join items i on c.itemid=i.itemid where c.userid=uuid_to_bin(%s)',[userid]) 
            cart_items=cursor.fetchall()
        else:
            itemid=data.get('itemid')
            quantity=int(data.get('quantity',1))
            cursor.execute('select bin_to_uuid(i.itemid),i.item_name,i.item_price,i.item_quantity,i.item_category,i.item_filename from items i where i.itemid=uuid_to_bin(%s)',[itemid]) 
            item=cursor.fetchone()
            if not item:
                return jsonify({
                    "status":"failed",
                    "message":"no item found"
                }),404
            availble_stock=item[3]
            if quantity>availble_stock:
                return jsonify({
                    "status":"failed",
                    "message":"Insufficient stock"
                })
            cart_items=[(item[0],item[1],item[2],quantity,item[4],item[5])]
        if not cart_items:
            return jsonify({
                "status":"failed",
                "message":'cart empty'
            }),404
        subtotal=0
        for item in cart_items:
            itemid=item[0]
            item_name=item[1]
            item_price=float(item[2])
            item_quantity=int(item[3])
            item_category=item[4]
            item_imgname=item[5]
            total=item_price*item_quantity
            subtotal += total
            image_url=url_for('static',filename=f'uploads/{item_imgname}',_external=True)            
        delivery=40
        tax=round(subtotal*0.05,2)
        grand_total=subtotal+tax+delivery
        #---- store the order info in orders
        cursor.execute('''insert  into orders(razorpay_orderid,razorpay_paymentid,userid,total_amount,delivery,tax,grand_total) values(%s,%s,uuid_to_bin(%s),%s,%s,%s,%s)''',[order_id,payment_id,userid,subtotal,delivery,tax,grand_total])
        order_table_id=cursor.lastrowid
        #-----------orderitems_details
        insert_items_query='''insert into orderitems_details(orderid,itemid,item_name,item_price,item_quantity,sub_total,item_category,item_filename) values(%s,uuid_to_bin(%s),%s,%s,%s,%s,%s,%s)'''
        ordered_items=[]
        for item in cart_items:
            itemid=item[0]
            item_name=item[1]
            item_price=float(item[2])
            item_quantity=int(item[3])
            item_category=item[4]
            item_imgname=item[5]
            total=item_price*item_quantity
            cursor.execute(insert_items_query,[order_table_id,str(itemid),item_name,item_price,item_quantity,total,item_category,item_imgname])
            cursor.execute('''update items set item_quantity=item_quantity-%s where itemid=uuid_to_bin(%s)''',[item_quantity,itemid])
            ordered_items.append({
                'itemid':itemid,
                'itemname':item_name,
                'price':item_price,
                'quantity':item_quantity,
                'subtotal':total
            })
        if mode=='cart':
            cursor.execute('delete from cart where userid=uuid_to_bin(%s)',[userid])
        mydb.commit()

        #------- success response
        return jsonify({
            "status":"success",
            "message":"payment verified successfully",
            "payment":{"payment_id":payment_id,"order_id":order_id},
            "summary":{
                "subtotal":subtotal,
                "delivery":delivery,
                "tax":tax,
                "grand_total":grand_total
            },
            "order_items":ordered_items
        }),200
    except Exception as e:
        mydb.rollback()
        print('Mysql error ',str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#my orders items
@app.route('/api/myorders',methods=['GET'])
def myorders():
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                "status":"failed",
                "message":"pls login first"
            }),401
        #mysql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        cursor.execute('select orderid,razorpay_orderid,razorpay_paymentid,total_amount,delivery,tax,grand_total,status,created_at from orders where userid=uuid_to_bin(%s)',[userid])
        orders=cursor.fetchall()
        all_orders=[]
        for order in orders:
            orderid=order[0]
            cursor.execute('select bin_to_uuid(itemid),item_name,item_price,item_quantity,sub_total,item_category,item_filename from orderitems_details where orderid=%s',[orderid])
            items=cursor.fetchall()
            order_items=[]
            for item in items:
                image_url=url_for('static',filename=f'uploads/{item[6]}',_external=True)
                order_items.append({
                    'itemid':item[0],
                    'itemname':item[1],
                    'price':float(item[2]),
                    'quantity':item[3],
                    'subtotal':float(item[4]),
                    'category':item[5],
                    'image':image_url
                })
            all_orders.append({
                'orderid':orderid,
                "razorpay_order_id":order[1],
                "razorpay_payment_id":order[2],
                "subtotal":float(order[3]),
                "delivery":float(order[4]),
                "tax":float(order[5]),
                "grand_total":float(order[6]),
                "created_at":str(order[7]),
                "items":order_items
            })
        return jsonify({
            "status":"success",
            "orders":all_orders
        }),200
    except Exception as e:
        print('Mysql error ',str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()
        
#my order details
@app.route('/api/orders/<ordid>',methods=['GET'])
def myorder_details(ordid):
    cursor=None
    try:
        if 'userid' not in session:
            return jsonify({
                "status":"failed",
                "message":"pls login first"
            }),401
        #mysql connection
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        userid=session.get('userid')
        cursor.execute('select orderid,razorpay_orderid,razorpay_paymentid,total_amount,delivery,tax,grand_total,status,created_at from orders where userid=uuid_to_bin(%s) and orderid=%s',[userid,ordid])
        order_data=cursor.fetchone()
        if not order_data:
            return jsonify({
                "status":"failed",
                "message":"order not found"
            }),401
        cursor.execute('select order_detailsid,orderid,bin_to_uuid(itemid),item_name,item_price,item_quantity,sub_total,item_category,item_filename from orderitems_details where orderid=%s',[ordid])
        orders_itemsdata=cursor.fetchall()
        #---------------format order
        order_json={
            'orderid':order_data[0],
            "razorpay_order_id":order_data[1],
            "razorpay_payment_id":order_data[2],
            "total_amount":float(order_data[3]),
            "delivery":float(order_data[4]),
            "tax":float(order_data[5]),
            "grand_total":float(order_data[6]),
            "created_at":str(order_data[7])
        }
        #--------------items format---------
        items_json=[]
        for item in orders_itemsdata:
            image_url=url_for('static',filename=f'uploads/{item[8]}',_external=True)
            items_json.append({
                'order_details_id':item[0],
                'order_id':item[1],
                'itemid':item[2],
                'item_name':item[3],
                'item_price':float(item[4]),
                'item_quantity':item[5],
                'subtotal':float(item[6]),
                'item_category':item[7],
                'item_image':image_url
            }
            )
        return jsonify({
            "status":"success",
            "order":order_json,
            "items":items_json
        }),200
    except Exception as e:
        print('Mysql error ',str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        }),500
    finally:
        if cursor:
            cursor.close()

#categories
@app.route('/api/category/<ctype>',methods=['GET'])
def category(ctype):
    cursor=None
    try:
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('''select bin_to_uuid(itemid),item_name,item_description,item_about,item_price,item_quantity,item_category,item_filename from items where item_category=%s''',[ctype])
        items_data=cursor.fetchall() #[(item1,),(item2)]
        if not items_data:
            return jsonify({
                "status":"failed",
                "message":"No items found"
            }),404
        products=[]
        for item in items_data:
            products.append({
                'itemid':item[0],
                'itemname':item[1],
                'description':item[2],
                'about':item[3],
                'price':float(item[4]),
                'quantity':item[5],
                'category':item[6],
                'image':url_for('static',filename=f'uploads/{item[7]}',_external=True)
            })
        return jsonify({
                'status':'success',
                'category':ctype,
                'message':f'All Items data',
                'total_items':len(products),
                'products':products
            }),200
    except Exception as e:
         print('CATEGORY ERROR:',str(e))
         return jsonify({
                'status':'failed',
                'message':f'{str(e)}'
            }),500
    finally:
        if cursor:
            cursor.close()

#User search
@app.route('/api/search',methods=['GET'])
def usersearch():
    cursor=None
    try:
        #get search query from url
        searchdata=request.args.get('q','').strip()
        #empty validation
        if not searchdata:
            return jsonify({
                "status":"failed",
                "message":"search query required"
            }),400
        #regex validation
        pattern =re.compile(r'^[A-Za-z0-9]+$',re.IGNORECASE)
        if not pattern.match(searchdata):
            return jsonify({
                "status":"failed",
                "message":"Invalid search"
            }),401
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('''select bin_to_uuid(itemid),item_name,item_description,item_about,item_price,item_quantity,item_category,item_filename from items where item_name like %s or item_description like %s or item_price like %s or item_category like %s''',[searchdata+'%','%'+searchdata+'%','%'+searchdata+'%','%'+searchdata+'%'])
        items_data=cursor.fetchall() #[(item1,),(item2)]
        if not items_data:
            return jsonify({
                "status":"failed",
                "message":"No items found"
            }),404
        items=[]
        for item in items_data:
            items.append({
                'itemid':item[0],
                'itemname':item[1],
                'description':item[2],
                'about':item[3],
                'price':float(item[4]),
                'quantity':item[5],
                'category':item[6],
                'image':url_for('static',filename=f'uploads/{item[7]}',_external=True)
            })
        return jsonify({
            "status":"success",
            "total_items":len(items),
            "items":items
        }),200
    except Exception as e:
         print('search ERROR:',str(e))
         return jsonify({
                'status':'failed',
                'message':f'{str(e)}'
            }),500
    finally:
        if cursor:
            cursor.close()

#Invoice generation
@app.route(
    '/api/invoice/<int:ord_id>',
    methods=['GET']
)
def get_invoice(ord_id):

    cursor = None

    try:

        # ---------------- LOGIN CHECK ----------------
        if 'userid' not in session:

            return jsonify({

                'status': 'failed',

                'message': 'Please login first'

            }), 401


        # reconnect automatically if mysql connection lost
        mydb.ping(reconnect=True)

        cursor = mydb.cursor(buffered=True)


        userid = session.get('userid')


        # ---------------- GET ORDER ----------------
        cursor.execute(
            '''
            SELECT

                orderid,
                razorpay_orderid,
                razorpay_paymentid,
                total_amount,
                delivery,
                tax,
                grand_total,
                created_at

            FROM orders

            WHERE userid=uuid_to_bin(%s)
            AND orderid=%s
            ''',
            [userid, ord_id]
        )

        order_data = cursor.fetchone()


        if not order_data:

            return jsonify({

                'status': 'failed',

                'message': 'Order not found'

            }), 404


        # ---------------- GET ORDER ITEMS ----------------
        cursor.execute(
            '''
            SELECT

                item_name,
                item_price,
                item_quantity,
                sub_total,
                item_category

            FROM orderitems_details

            WHERE orderid=%s
            ''',
            [ord_id]
        )

        order_items = cursor.fetchall()


        # ---------------- CREATE PDF BUFFER ----------------
        pdf_buffer = BytesIO()


        # ---------------- CREATE DOCUMENT ----------------
        doc = SimpleDocTemplate(

            pdf_buffer,

            pagesize=A4,

            rightMargin=30,

            leftMargin=30,

            topMargin=30,

            bottomMargin=20
        )


        styles = getSampleStyleSheet()

        elements = []


        # ---------------- TITLE ----------------
        title = Paragraph(

            "<b>BUYROUTE INVOICE</b>",

            styles['Title']
        )

        elements.append(title)

        elements.append(Spacer(1, 15))


        # ---------------- ORDER DETAILS ----------------
        order_info = f"""

        <b>Order ID:</b> {order_data[0]} <br/>

        <b>Razorpay Order ID:</b> {order_data[1]} <br/>

        <b>Payment ID:</b> {order_data[2]} <br/>

        <b>Order Date:</b> {order_data[7]} <br/>

        """


        order_para = Paragraph(

            order_info,

            styles['BodyText']
        )

        elements.append(order_para)

        elements.append(Spacer(1, 10))

        elements.append(HRFlowable(width="100%"))

        elements.append(Spacer(1, 15))


        # ---------------- TABLE DATA ----------------
        table_data = [[

            'Item Name',

            'Category',

            'Price',

            'Quantity',

            'Subtotal'
        ]]


        for item in order_items:

            table_data.append([

                item[0][0:20],

                item[4][0:20],

                f"₹{float(item[1])}",

                str(item[2]),

                f"₹{float(item[3])}"
            ])


        # ---------------- CREATE TABLE ----------------
        table = Table(

            table_data,

            colWidths=[180, 100, 80, 70, 80]
        )


        # ---------------- TABLE STYLE ----------------
        table.setStyle(

            TableStyle([

                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),

                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                ('FONTSIZE', (0, 0), (-1, -1), 10),

                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),

                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

                ('ALIGN', (2, 1), (-1, -1), 'CENTER')
            ])
        )

        elements.append(table)

        elements.append(Spacer(1, 20))


        # ---------------- SUMMARY ----------------
        summary = f"""

        <b>Items Total:</b> ₹{float(order_data[3])}<br/><br/>

        <b>Delivery:</b> ₹{float(order_data[4])}<br/><br/>

        <b>Tax:</b> ₹{float(order_data[5])}<br/><br/>

        <b>Grand Total:</b> ₹{float(order_data[6])}

        """


        summary_para = Paragraph(

            summary,

            styles['Heading3']
        )

        elements.append(summary_para)

        elements.append(Spacer(1, 25))


        # ---------------- FOOTER ----------------
        footer = Paragraph(

            "Thank you for shopping with BUYROUTE",

            styles['Italic']
        )

        elements.append(footer)


        # ---------------- BUILD PDF ----------------
        doc.build(elements)

        pdf_buffer.seek(0)


        # ---------------- RESPONSE ----------------
        response = make_response(

            pdf_buffer.getvalue()
        )

        response.headers['Content-Type'] = 'application/pdf'

        response.headers['Content-Disposition'] = (

            f'attachment; filename=invoice_{ord_id}.pdf'
        )

        return response


    except Exception as e:

        print(f'Invoice Error: {e}')

        return jsonify({

            'status': 'failed',

            'message': str(e)

        }), 500


    finally:

        if cursor:
            cursor.close()



#forgot password
@app.route('/api/forgotpassword',methods=['POST'])
def forgotpassword():
    try:
        data=request.get_json() #useremail
        if not data:
            return jsonify({"status":"failed","message":"User email required"}),401
        f_email=data.get('email')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select count(*) from userdata where useremail=%s",[f_email])
        count_email=cursor.fetchone() #(1,) or(0,) or "none"
        if count_email[0]==1:
            reset_link=f"{url_for('resetpassword',token=endata(f_email),_external=True)}"
            subject="Reset password link"
            body=f"Click the link to reset password:\n {reset_link}"
            send_mail(to=f_email,body=body,subject=subject)
            return jsonify({
                "status":"success",
                "message":"Reset link sent successfully"
            }),200
        else:
            return jsonify({
                "status":"failed",
                "message":"USer not Found"
            }),400
    except Exception as e:
        print("Mysql error",str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        })
    finally:
        if cursor:
            cursor.close()

#reset link
@app.route('/api/resetpassword/<token>',methods=['POST'])
def resetpassword(token):
    try:
        data=request.get_json()
        if not data:
            return jsonify({
                "status":"failed",
                "message":"No input given"
            })
        npassword=data.get('password')
        cpassword=data.get('confirm_password')
        if npassword!=cpassword:
            return jsonify({
                "status":"failed",
                "message":"Password Mismatch"
            }),401
        email=dndata(token)
        hashed_pwd=bcrypt.generate_password_hash(npassword)
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select count(*) from userdata where useremail=%s",[email])
        count_email=cursor.fetchone() #(1,) or(0,) or "none"
        if count_email[0]==0:
            return jsonify({
                "status":"failed",
                "message":"Email not found"
            }),401
        cursor.execute('update userdata set userpassword=%s where useremail=%s',[hashed_pwd,email])
        mydb.commit()
        return jsonify({
            "status":"success", 
            "message":"Password updated successfully"
        }),200
    except Exception as e:
        print("Mysql error",str(e))
        return jsonify({
            "status":"failed",
            "message":f"{str(e)}"
        })
    finally:
        if cursor:
            cursor.close()



if __name__ == "__main__":
    app.run()