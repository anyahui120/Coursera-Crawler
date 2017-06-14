# Coursera-Crawler
A crawler for Coursera
This is a simple crawler for coursera.

1. Enviroment setup

      1.1 Python 2.7(Recommend to install anaconda)
  
      1.2 Install some packages included in requirements.txt
  
	      pip install -r requirements.txt
  
      1.3 Download Phantomjs from website, install it and write the installed path to config.yml

2. config.yml

	"UserName" is the username for coursera account;
	
	"Password" is the password for coursera account;
	
	"UserId" is the ID for every account.
	    
	    First, you have to login using your coursera account on the website. Then press F12, select "Network" and choose XHR. 
	    
	    You can see an API link "https://www.coursera.org/api/openCourseMemberships.v1/?q=findByUser&userId=XXX", your userid is "XXX".
	
	"filePath" is the path to save the data you crawled.
  
        When you login, you will see "My Courses", including "Last Active" and "Inactive".
	"activeCoursePageNum" is the maximum pages of your "Last Active" courses you want to crawl.
	"inactiveCoursePageNum" is the maximum pages of your "Inactive" courses you want to crawl.

3. CourseraScraper.py

	python CourseraScraper.py
	The crawled data will be saved in folders. Every course has a folder named as courseName_courseID_crawlTime(%Y_%m_%d)
	


