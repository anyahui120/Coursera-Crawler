#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Time    : 10/19/2016 4:14 PM
# @Author  : Ann
# @Site    :
# @File    : CourseraScraper.py
# @Software: PyCharm

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import yaml
import json,string
import html.parser
import pycurl
import math
import StringIO
import certifi
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class CourseraScraper:
    """This class is for crawling all the data in the discussion forums of Coursera.
       Crawling courses that user has enrolled. 
       Crawling the threads, posts and users(learner, mentor, instructor and staff) of every course.
    """

    def __init__(self):
        """ Inits CourseraScraper with driver and user account information."""
        with open('config.yml') as f:
            config = yaml.load(f)
        self.driver = webdriver.PhantomJS()
        self.email = config['UserName']
        self.password = config['Password']
        self.courses = []

    def login(self):
        """Login Coursera using PhantomJS simulating web browser without a graphical user interface. """
        
        self.driver.get('https://www.coursera.org/?authMode=login')
        email_field = self.driver.find_element_by_name("email")
        password_field = self.driver.find_element_by_name("password")
        email_field.send_keys(self.email)
        password_field.send_keys(self.password)
        password_field.submit()

    def get_active_courses(self,activeCoursePageNum):
        """Courses are splitted into three types: "Last active", "Inactive" and "Completed".
           Get courseids of last active courses by parsing the first page.
        
        Args:
            activeCoursePageNum: the number(int) of pages of last active courses.
           
        Returns:
            active_course_ids: a list of course ids.
            course_id_and_name: a dict mapping course ids to the course names.
        
        """
     
        active_course_ids = []
        course_id_and_name = {}
        for i in range(1,(activeCoursePageNum+1),1):
            active_courses_url = 'https://www.coursera.org/?page=%d&skipRecommendationsRedirect=true&tab=current' % i
            self.driver.get(active_courses_url)
            html = self.driver.page_source
            html = str(html)

            soup = BeautifulSoup(html,'html.parser')
            active_course_links = soup.findAll('ul')
            for course in active_course_links:
                if course.attrs['class'] == ['styleguide', 'dropdown', 'bt3-dropdown-menu']:
                    #get courseId
                    CourseId = str(course.attrs['id'])
                    CourseId = CourseId.replace('dropdown-','')
                    CourseName_link = course.contents[0].contents[0]['href']
                    #get courseName
                    CourseName = CourseName_link.replace('/learn/','')
                    CourseName = CourseName.replace('/home','')
                    active_course_ids.append(CourseId)
                    course_id_and_name[CourseId] = CourseName
                else:
                    continue
            self.driver.back()

        return active_course_ids, course_id_and_name

    def get_inactive_courses(self,inactiveCoursePageNum):
        """Courses are splitted into three types: "Last active", "Inactive" and "Completed".
           Get courseids of  inactive courses by parsing the first page.
        
        Args:
            inactiveCoursePageNum: the number(int) of pages of inactive courses.
           
        Returns:
            inactive_course_ids: a list of course ids.
            course_id_and_name: a dict mapping course ids to the course names.
        
        """
        inactive_course_ids = []
        course_id_and_name = {}
        for i in range(1,(inactiveCoursePageNum+1),1):
            inactive_courses_url = 'https://www.coursera.org/?page=%d&skipRecommendationsRedirect=true&tab=inactive' % i
            self.driver.get(inactive_courses_url)
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            inactive_course_links = soup.findAll('ul')
            for course in inactive_course_links:
                if course.attrs['class'] == ['styleguide', 'dropdown', 'bt3-dropdown-menu']:
                    # get courseId
                    CourseId = str(course.attrs['id'])
                    CourseId = CourseId.replace('dropdown-', '')
                    CourseName_link = course.contents[0].contents[0]['href']
                    # get courseName
                    CourseName = CourseName_link.replace('/learn/', '')
                    CourseName = CourseName.replace('/home', '')
                    ss = '/course/'
                    if (string.find(CourseName, ss) != -1):
                        continue
                    else:
                        inactive_course_ids.append(CourseId)
                        course_id_and_name[CourseId] = CourseName
                else:
                    continue
            self.driver.back()
        return inactive_course_ids, course_id_and_name

    def get_cookie(self,CourseName):
        new_url = 'https://www.coursera.org/learn/%s/discussions/all' %CourseName
        # course_discussion_urls.append(new_url)
        self.driver.get(new_url)
        # get current cookie and save as file
        cookie_items = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        cookie = ';'.join(item for item in cookie_items)
        return cookie

    def get_courseforum_id(self,COURSEID,COURSENAME,cookie):
        """Get course_forum_id for constructing the API of threads.
        
        Args:
            COURSEID: the id of the course(String), geting this value from get_active_courses() or get_inactive_courses().
            COURSENAME: the name of the course(String), geting this value from get_active_courses() or get_inactive_courses().
            cookie: the cookie for visiting the course discussion page.
            
        Returns:
            rootCourseForumId: An id(String) for constructing the API of threads in next step.
        """
        ForumUrlAPI = 'https://www.coursera.org/api/onDemandCourseForums.v1?q=course&courseId=%s&limit=500&fields=title,description,parentForumId,order,legacyForumId,forumType,forumQuestionCount,lastAnsweredAt,groupForums.v1(title,description,parentForumId,order,forumType)' % COURSEID
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, ForumUrlAPI)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)
        rootCourseForumId = ''
        if code == 200:
            json_data = b.getvalue()
            elements = json.loads(json_data)['elements']

            for e in range(len(elements)):
                # forumQuestionCount = elements[e]['forumQuestionCount']
                forumType = str(elements[e]['forumType']['typeName'])
                # if (forumQuestionCount !=0 ):
                if (forumType == 'rootForumType'):
                    rootCourseForumId = elements[e]['id']
                    break
                else:
                    continue
            return rootCourseForumId
        else:
            print "This course's discussion gone!"
            return rootCourseForumId

    def get_thread_info(self, rootCourseForumId, cookie,fileout,userId):
        """Get thread information and write into file with json format.
        
        Args:
            rootCourseForumId: An id(String) for constructing the API of threads.
            cookie: the cookie for visiting the course discussion page.
            fileout: the open file for writing thread data.
            userId: id for user account got by analysing the APIs. 
            
        Returns:
            threadsIdList: A list of thread id for constructing the API of posts in the next step.
        """
        # get all the threads info available(the original post page info)
        threadsIdList = []
        threadUrl = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/?userId=%s&shouldAggregate=true&includeDeleted=false&sort=lastActivityAtDesc&fields=content%%2Cstate%%2CcreatorId%%2CcreatedAt%%2CforumId%%2CsessionId%%2ClastAnsweredBy%%2ClastAnsweredAt%%2CupvoteCount%%2CfollowCount%%2CtotalAnswerCount%%2CtopLevelAnswerCount%%2CviewCount%%2CanswerBadge%%2CisFlagged%%2CisUpvoted%%2CisFollowing%%2ConDemandSocialProfiles.v1(userId%%2CexternalUserId%%2CfullName%%2CphotoUrl%%2CcourseRole)&includes=profiles&limit=15&q=byCourseForumId&courseForumId=%s' % (userId,rootCourseForumId)
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, threadUrl)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        json_data = b.getvalue()
        #需要建立一个list来存储threadid 注意翻页

        threads = json.loads(json_data)['elements']
        for i in range(len(threads)):
            thread = threads[i]
            fileout.write(json.dumps(thread, encoding='utf-8'))
            fileout.write('\n')
            threadId = json.loads(json_data)['elements'][i]['id']
            threadsIdList.append(threadId)
        b.close()
        c.close()
        totalThreadsCount = json.loads(json_data)['paging']['total']
        total_num = totalThreadsCount
        loop_num = int(math.floor((total_num - 1) / 15))
        for i in range(1,loop_num+1,1):
            start_page = (i) * 15
            new_threadURL = threadUrl + '&start=%d' % start_page
            # get all the posts left
            c = pycurl.Curl()
            b = StringIO.StringIO()
            c.setopt(pycurl.CAINFO, certifi.where())
            c.setopt(c.URL, new_threadURL)
            c.setopt(pycurl.CUSTOMREQUEST, 'GET')
            c.setopt(c.WRITEFUNCTION, b.write)
            c.setopt(pycurl.COOKIE, cookie)
            c.perform()
            c.setopt(pycurl.COOKIE, cookie)
            json_data = b.getvalue()
            b.close()
            c.close()
            threads = json.loads(json_data)['elements']
            for i in range(len(threads)):
                thread = threads[i]
                fileout.write(json.dumps(thread, encoding='utf-8'))
                fileout.write('\n')
                threadId = json.loads(json_data)['elements'][i]['id']
                threadsIdList.append(threadId)
            b.close()
            c.close()

        return threadsIdList

    def get_posts(self,threadId,cookie,fileoutPost,fileoutUser):
        """Get post and user information and write into file with json format.
        
        Args:
            threadId: An thread id(String) for constructing the API of posts.
            cookie: the cookie for visiting the course discussion page.
            fileoutPost: the open file for writing posts data.
            fileoutUser: the open file for writing users data. 
            
        """
        postURL = 'https://www.coursera.org/api/onDemandCourseForumAnswers.v1/?q=byForumQuestionId&includeDeleted=false&fields=content%%2CforumQuestionId%%2CparentForumAnswerId%%2Cstate%%2CcreatorId%%2CcreatedAt%%2Corder%%2CupvoteCount%%2CchildAnswerCount%%2CisFlagged%%2CisUpvoted%%2ConDemandSocialProfiles.v1(userId%%2CexternalUserId%%2CfullName%%2CphotoUrl%%2CcourseRole)%%2ConDemandCourseForumAnswers.v1(content%%2CforumQuestionId%%2CparentForumAnswerId%%2Cstate%%2CcreatorId%%2CcreatedAt%%2Corder%%2CupvoteCount%%2CchildAnswerCount%%2CisFlagged%%2CisUpvoted)&includes=profiles%%2Cchildren&limit=15&userCourseQuestionId=%s&sort=createdAtDesc' % threadId
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, postURL)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        json_data = b.getvalue()
        #Get total num and all the limited posts from postURL{elements:[], linked:{}, paging:{next:"15",total:20}}
        totalAnswerCount = json.loads(json_data)['paging']['total']
        posts = json.loads(json_data)['elements']
        childPosts = json.loads(json_data)['linked']['onDemandCourseForumAnswers.v1']
        users = json.loads(json_data)['linked']['onDemandSocialProfiles.v1']
        b.close()
        c.close()
        for j in range(len(posts)):
            post = posts[j]
            fileoutPost.write(json.dumps(post, encoding='utf-8'))
            fileoutPost.write('\n')
        for jj in range(len(users)):
            user = users[jj]
            fileoutUser.write(json.dumps(user, encoding='utf-8'))
            fileoutUser.write('\n')
        for jjj in range(len(childPosts)):
            childPost = childPosts[jjj]
            fileoutPost.write(json.dumps(childPost, encoding='utf-8'))
            fileoutPost.write('\n')
        total_num = totalAnswerCount
        loop_num = int(math.floor((total_num - 1) / 15))

        for i in range(1,loop_num+1,1):
            start_page = i * 15
            new_postURL = postURL + '&start=%d' % start_page
            #get all the posts left
            c = pycurl.Curl()
            b = StringIO.StringIO()
            c.setopt(pycurl.CAINFO, certifi.where())
            c.setopt(c.URL, new_postURL)
            c.setopt(pycurl.CUSTOMREQUEST, 'GET')
            c.setopt(c.WRITEFUNCTION, b.write)
            c.setopt(pycurl.COOKIE, cookie)
            c.perform()
            c.setopt(pycurl.COOKIE, cookie)
            json_data = b.getvalue()
            posts = json.loads(json_data)['elements']
            users = json.loads(json_data)['linked']['onDemandSocialProfiles.v1']
            b.close()
            c.close()
            for j in range(len(posts)):
                post = posts[j]
                fileoutPost.write(json.dumps(post, encoding='utf-8'))
                fileoutPost.write('\n')
            for jj in range(len(users)):
                user = users[jj]
                fileoutUser.write(json.dumps(user, encoding='utf-8'))
                fileoutUser.write('\n')
            for jjj in range(len(childPosts)):
                childPost = childPosts[jjj]
                fileoutPost.write(json.dumps(childPost, encoding='utf-8'))
                fileoutPost.write('\n')
    
    def writeToSql(self):
        pass

if __name__ == "__main__":
    try:
        scraper = CourseraScraper()
        scraper.driver.implicitly_wait(10)
        scraper.login()
        time.sleep(2)
    except Exception, e:
        print e
        scraper.driver.close()
        scraper.driver.quit()

    with open('config.yml') as f:
        config = yaml.load(f)
    userId = config['UserId']
    filePath = config['filePath']
    # file1 = filePath + 'threads.json'
    # fileoutThread = open(file1,'w+')
    # file2 = filePath + 'posts.json'
    # fileoutPosts = open(file2,'w+')
    # file3 = filePath + 'users.json'
    # fileoutUsers = open(file3,'w+')


    try:
        activeCoursePageNum = config['activeCoursePageNum']
        active_course_ids, course_id_and_name = scraper.get_active_courses(activeCoursePageNum)
        for i in range(len(active_course_ids)):
            print 'Getting active courses!Total:%d...Processing:%d' % (len(active_course_ids),i+1)
            courseId = active_course_ids[i]
            courseName = course_id_and_name[courseId]

            newFilePath = filePath + str(courseName) + '_' + str(courseId) + '_' + str(time.strftime('%Y_%m_%d')) + '/'
            isExists = os.path.exists(newFilePath)
            if not isExists:
                os.mkdir(newFilePath)
            file1 = newFilePath + 'threads.json'
            fileoutThread = open(file1,'w+')
            file2 = newFilePath + 'posts.json'
            fileoutPosts = open(file2,'w+')
            file3 = newFilePath + 'users.json'
            fileoutUsers = open(file3,'w+')

            cookie = scraper.get_cookie(courseName)
            rootCourseForumId = scraper.get_courseforum_id(courseId,courseName,cookie=cookie)
            threadIdList = scraper.get_thread_info(rootCourseForumId,cookie,fileout=fileoutThread,userId=userId)
            for j in range(len(threadIdList)):
                threadId = threadIdList[j]
                post = scraper.get_posts(threadId,cookie,fileoutPost=fileoutPosts,fileoutUser=fileoutUsers)
            print 'Successfully get all the posts!'
            fileoutThread.close()
            fileoutPosts.close()
            fileoutUsers.close()
        #*******************************************************************************************************#
        inactiveCoursePageNum = config['inactiveCoursePageNum']
        print 'Getting inactive courses who have the discussion forum!'
        inactive_course_ids, course_id_and_name = scraper.get_inactive_courses(inactiveCoursePageNum)
        for i in range(len(inactive_course_ids)):
            print 'Getting inactive courses forum!Total:%d...Processing:%d' % (len(inactive_course_ids), i + 1)
            courseId = inactive_course_ids[i]
            courseName = course_id_and_name[courseId]

            newFilePath = filePath  + str(courseName) + '_'+ str(courseId) +'_' + str(time.strftime('%Y_%m_%d')) + '/'
            isExists = os.path.exists(newFilePath)
            if not isExists:
                os.mkdir(newFilePath)
            file1 = newFilePath + 'threads.json'
            fileoutThread = open(file1, 'w+')
            file2 = newFilePath + 'posts.json'
            fileoutPosts = open(file2, 'w+')
            file3 = newFilePath + 'users.json'
            fileoutUsers = open(file3, 'w+')


            cookie = scraper.get_cookie(courseName)
            rootCourseForumId = scraper.get_courseforum_id(courseId, courseName, cookie=cookie)
            if rootCourseForumId == '':
                print "Fail to get rootCourseForumId.Having no discussion data."
                print courseId,courseName
                continue
            threadIdList = scraper.get_thread_info(rootCourseForumId, cookie, fileout=fileoutThread,userId=userId)
            for j in range(len(threadIdList)):
                threadId = threadIdList[j]
                post = scraper.get_posts(threadId, cookie, fileoutPost=fileoutPosts, fileoutUser=fileoutUsers)
            print 'Successfully get all the posts!'
            fileoutUsers.close()
            fileoutPosts.close()
            fileoutThread.close()
    except Exception,e:
        print e
        scraper.driver.close()
        scraper.driver.quit()
    scraper.driver.close()
    scraper.driver.quit()
