from itsdangerous import URLSafeTimedSerializer
secret_key='code8989'
def endata(data):
    serializer=URLSafeTimedSerializer(secret_key)
    return serializer.dumps(data,salt='otpverify')
def dndata(data):
    serializer=URLSafeTimedSerializer(secret_key)
    return serializer.loads(data,salt='otpverify',max_age=180)#max age means the otp shpuld be entered within 1 min