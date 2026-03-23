# ============================================
# Frontend Dockerfile - Nginx로 정적 파일 서빙
# ============================================

FROM nginx:alpine

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 정적 파일 복사
COPY index.html /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY detail.html /usr/share/nginx/html/
COPY detail.js /usr/share/nginx/html/
COPY detail.css /usr/share/nginx/html/
COPY history.html /usr/share/nginx/html/
COPY history.js /usr/share/nginx/html/
COPY history.css /usr/share/nginx/html/
COPY market.html /usr/share/nginx/html/
COPY market.js /usr/share/nginx/html/
COPY market.css /usr/share/nginx/html/

RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
