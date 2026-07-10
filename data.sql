-- MySQL dump 10.13  Distrib 9.1.0, for Win64 (x86_64)
--
-- Host: localhost    Database: ecomdbOnr12
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admindata`
--

DROP TABLE IF EXISTS `admindata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admindata` (
  `adminid` binary(16) NOT NULL,
  `username` varchar(50) NOT NULL,
  `useremail` varchar(50) NOT NULL,
  `password` varbinary(255) NOT NULL,
  `agree` enum('on','off') DEFAULT NULL,
  `filename` varchar(20) DEFAULT NULL,
  `adminaddress` varchar(255) NOT NULL,
  `admin_phone` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`adminid`),
  UNIQUE KEY `useremail` (`useremail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admindata`
--

LOCK TABLES `admindata` WRITE;
/*!40000 ALTER TABLE `admindata` DISABLE KEYS */;
INSERT INTO `admindata` VALUES (_binary 'ºTR\åpS\ñš?\n\0\'\0\0','Sreeja Ramgari','sreejaramgari028@gmail.com',_binary '$2b$12$hqm81whQyKXLpFWtVPnxquugTM/yAJK4r37kOzwck7dPsXY3sR1ey','on',NULL,'KTR Colony Nizampet','');
/*!40000 ALTER TABLE `admindata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `cartid` binary(16) NOT NULL,
  `itemid` binary(16) DEFAULT NULL,
  `userid` binary(16) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  PRIMARY KEY (`cartid`),
  KEY `itemid` (`itemid`),
  KEY `userid` (`userid`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`itemid`) REFERENCES `items` (`itemid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `userdata` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (_binary '½\'•z\ñš?\n\0\'\0\0',_binary '’Æ§\âyh\ñš?\n\0\'\0\0',_binary 'Œ±\ÊGu\Ï\ñš?\n\0\'\0\0',1);
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `itemid` binary(16) NOT NULL,
  `item_name` longtext,
  `item_description` longtext,
  `item_about` longtext,
  `item_price` decimal(20,4) DEFAULT NULL,
  `item_quantity` int unsigned DEFAULT NULL,
  `item_category` enum('home_appliences','grocery','Fashion','Electronics','sports','toys') DEFAULT NULL,
  `added_by` binary(16) DEFAULT NULL,
  `item_filename` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`itemid`),
  KEY `added_by` (`added_by`),
  CONSTRAINT `items_ibfk_1` FOREIGN KEY (`added_by`) REFERENCES `admindata` (`adminid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (_binary '=\0|‡t³\ñš?\n\0\'\0\0','TrustBasket Blossom','Material	Polymer\nColour	White\nSpecial Feature	UV Resistant, Mess-Free Watering, Easy Drainage\nStyle	18 inch\nPlanter Form	Plant Pot','Durable and Spacious Jumbo Plant Pot: The TrustBasket Blossom Pot is a perfect choice for those seeking jumbo plant pots and big pots with excellent durability. Its 18-inch size provides ample space for plant roots to spread, making it one of the most reliable big pot for indoor plants. UV-protected and lightweight, it\'s ideal for all weather conditions and can be used as big planters for home decor both indoors and outdoors.',1000.0000,599,'home_appliences',_binary 'ºTR\åpS\ñš?\n\0\'\0\0','Z4lP9o.webp','2026-07-01 00:10:59'),(_binary '’Æ§\âyh\ñš?\n\0\'\0\0','Kids Phone â€“ Rechargeable Toy for Kids with 24 Learning Modes | Talking Dummy Mobile for Boys & Girls Age 2â€“12 | Educational Mobile Phone Toy with, Music & Games Flash Card Phone','Brand	LYNREX\r\nSize	Flash Card Phone\r\nMaterial	Paper\r\nEducational Objective	Cognitive Skills\r\nTheme	Animals','ğŸ“± Interactive Kids Phone with 24 Learning Modes: This realistic toy phone for kids is packed with 24 engaging functions such as music, stories, animals, fruits, body parts, colors, numbers, transport, nature sounds, and more. Designed to look and feel like a real smartphone, itâ€™s ideal for encouraging roleplay and boosting cognitive development in children ages 2 to 12.',374.0000,1,'toys',_binary 'ºTR\åpS\ñš?\n\0\'\0\0','A1sE4f.webp','2026-07-06 23:59:07'),(_binary '\Ê\ë\Óyg\ñš?\n\0\'\0\0','WonderBuddy Divine Mantra Chanting Baby Krishna with 8 Preloaded Mantras & Aartis, Musical Soft Plush Toy, Best Birthday Gift for Infants, Toddlers & Kids (Medium - 28 Cm)','ğ——ğ—¶ğ˜ƒğ—¶ğ—»ğ—² ğ—•ğ—²ğ—´ğ—¶ğ—»ğ—»ğ—¶ğ—»ğ—´ğ˜€ â€” Specially designed for Newborns, Infants & Toddlers (0â€“5 years), these soft, huggable plush toys come preloaded with soothing mantras & aartis to introduce your child to Indian culture and heritage.\r\n8 ğ—ğ—¿ğ—¶ğ˜€ğ—µğ—»ğ—® ğ— ğ—²ğ—¹ğ—¼ğ—±ğ—¶ğ—²ğ˜€ ğ—œğ—»ğ˜€ğ—¶ğ—±ğ—² â€” Includes 8 Krishna mantras, aartis, chaupais, and bhajans to create peaceful, culturally rooted moments anytime, anywhere.','ğ—¿ğ—¼ğ—º ğ—§ğ—®ğ—»ğ˜ğ—¿ğ˜‚ğ—ºğ˜€ ğ˜ğ—¼ ğ—§ğ—¿ğ—®ğ—»ğ—¾ğ˜‚ğ—¶ğ—¹ğ—¶ğ˜ğ˜† â€” A blend of sacred sounds and cuddly comfort that helps calm little ones anytime, anywhere. Perfect for emotional regulation and peaceful routines.\r\nğ— ğ—¶ğ—»ğ—±ğ—³ğ˜‚ğ—¹ ğ—£ğ—¹ğ—®ğ˜† & ğ—•ğ—¼ğ—»ğ—±ğ—¶ğ—»ğ—´ â€” Ideal for bedtime, morning routies, aartis, poojas, travel, and quiet play. Encourages cultural curiosity and early connection to tradition in the most natural, child-friendly way.',1197.0000,2,'toys',_binary 'ºTR\åpS\ñš?\n\0\'\0\0','P2mN7u.webp','2026-07-06 23:53:31');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderitems_details`
--

DROP TABLE IF EXISTS `orderitems_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderitems_details` (
  `order_detailsid` int unsigned NOT NULL AUTO_INCREMENT,
  `orderid` int unsigned DEFAULT NULL,
  `itemid` binary(16) DEFAULT NULL,
  `item_name` longtext,
  `item_price` decimal(10,2) DEFAULT NULL,
  `item_quantity` int unsigned DEFAULT NULL,
  `sub_total` decimal(10,2) DEFAULT NULL,
  `item_category` enum('home_appliences','grocery','fashion','electronics','sports','toys') DEFAULT NULL,
  `item_filename` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`order_detailsid`),
  KEY `itemid` (`itemid`),
  KEY `orderid` (`orderid`),
  CONSTRAINT `orderitems_details_ibfk_1` FOREIGN KEY (`itemid`) REFERENCES `items` (`itemid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `orderitems_details_ibfk_2` FOREIGN KEY (`orderid`) REFERENCES `orders` (`orderid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderitems_details`
--

LOCK TABLES `orderitems_details` WRITE;
/*!40000 ALTER TABLE `orderitems_details` DISABLE KEYS */;
INSERT INTO `orderitems_details` VALUES (1,1,_binary '=\0|‡t³\ñš?\n\0\'\0\0','TrustBasket Blossom',1000.00,1,1000.00,'home_appliences','Z4lP9o.webp'),(2,1,_binary '’Æ§\âyh\ñš?\n\0\'\0\0','Kids Phone â€“ Rechargeable Toy for Kids with 24 Learning Modes | Talking Dummy Mobile for Boys & Girls Age 2â€“12 | Educational Mobile Phone Toy with, Music & Games Flash Card Phone',374.00,1,374.00,'toys','A1sE4f.webp'),(3,1,_binary '\Ê\ë\Óyg\ñš?\n\0\'\0\0','WonderBuddy Divine Mantra Chanting Baby Krishna with 8 Preloaded Mantras & Aartis, Musical Soft Plush Toy, Best Birthday Gift for Infants, Toddlers & Kids (Medium - 28 Cm)',1197.00,1,1197.00,'toys','P2mN7u.webp');
/*!40000 ALTER TABLE `orderitems_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `orderid` int unsigned NOT NULL AUTO_INCREMENT,
  `razorpay_orderid` varchar(100) DEFAULT NULL,
  `razorpay_paymentid` varchar(100) DEFAULT NULL,
  `userid` binary(16) DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `delivery` int unsigned DEFAULT NULL,
  `tax` decimal(10,2) DEFAULT NULL,
  `grand_total` decimal(10,2) DEFAULT NULL,
  `status` varchar(30) DEFAULT 'paid',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`orderid`),
  KEY `userid` (`userid`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `userdata` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'order_TAUTUK1o2ElXrM','pay_TAUU4jA7bNBDeD',_binary 'Œ±\ÊGu\Ï\ñš?\n\0\'\0\0',2571.00,40,128.55,2739.55,'paid','2026-07-07 10:34:48');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userdata`
--

DROP TABLE IF EXISTS `userdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userdata` (
  `userid` binary(16) NOT NULL,
  `username` varchar(50) NOT NULL,
  `useremail` varchar(50) NOT NULL,
  `useraddress` varchar(255) DEFAULT NULL,
  `userpassword` varbinary(255) DEFAULT NULL,
  `userphone` varchar(12) DEFAULT NULL,
  `usergender` enum('Female','Male','Others') DEFAULT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `useremail` (`useremail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userdata`
--

LOCK TABLES `userdata` WRITE;
/*!40000 ALTER TABLE `userdata` DISABLE KEYS */;
INSERT INTO `userdata` VALUES (_binary 'Œ±\ÊGu\Ï\ñš?\n\0\'\0\0','Sreeja','sreejaramgari028@gmail.com','Medak',_binary '$2b$12$vfhvIFr0y.NGRrGJIj6I/uRiOTOtH8wSXGYnnfIxIY6asZPCp8oXa','1234567890','Female');
/*!40000 ALTER TABLE `userdata` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-10 18:27:47
