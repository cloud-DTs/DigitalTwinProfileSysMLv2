#!/bin/bash
set -e
RELEASE=${API_RELEASE:-2025-02}
wget -q https://github.com/Systems-Modeling/SysML-v2-API-Services/archive/${RELEASE}.tar.gz -O ${RELEASE}.tar.gz
tar xfz ${RELEASE}.tar.gz --strip-components=0

cd SysML-v2-API-Services-${RELEASE} || exit 1

sed -i 's/key=.whatever./key="longersecretnowarnings"/' conf/application.conf
echo -e "\nplay.filters.hosts {\n   allowed = [\"$API_SYSML_API_SERVER_URL\", \"localhost:9000\"]\n}" >> conf/application.conf


DB_SERVER_URL="jdbc:postgresql://postgresdbserver:5432/$POSTGRES_DB"
xmlstarlet ed --inplace -u '_:persistence/_:persistence-unit/_:properties/_:property[@name="javax.persistence.jdbc.url"]/@value' -v "$DB_SERVER_URL" conf/META-INF/persistence.xml
xmlstarlet ed --inplace -u '_:persistence/_:persistence-unit/_:properties/_:property[@name="javax.persistence.jdbc.user"]/@value' -v "$POSTGRES_USER" conf/META-INF/persistence.xml
xmlstarlet ed --inplace -u '_:persistence/_:persistence-unit/_:properties/_:property[@name="javax.persistence.jdbc.password"]/@value' -v "$POSTGRES_PASSWORD" conf/META-INF/persistence.xml
xmlstarlet ed --inplace -u '_:persistence/_:persistence-unit/_:properties/_:property[@name="hibernate.hbm2ddl.auto"]/@value' -v "update" conf/META-INF/persistence.xml

exec sbt run

