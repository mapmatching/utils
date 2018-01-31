FROM tomcat:8

ADD dist/star-search-api.war /usr/local/tomcat/webapps/ROOT.war

ADD docker-entrypoint.sh /

RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["catalina.sh","run"]
