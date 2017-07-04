# Coursera-Crawler
A crawler to scrape Coursera's discussion forum.

High-level code flow is documented <a href="https://github.com/anyahui120/Coursera-Crawler/blob/master/diagram.jpg"> here</a>.

1. Enviroment setup

      1.1 Python 2.7 (We recommend to set it up with anaconda)
  
      1.2 Install the packages specified in requirements.txt
  
	      pip install -r requirements.txt
  
      1.3 Download Phantomjs <a href="https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip"> here</a> for Windows, <a href="https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-macosx.zip"> here</a> for MacOS and <a href="https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"> here</a> for Linux-64 bit( <a href="http://phantomjs.org/download.html"> Other references</a>), install it and write the path to config.yml.

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
