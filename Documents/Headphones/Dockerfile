# Use a lightweight Nginx image to serve the static website
FROM nginx:alpine

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy all HTML files to the Nginx serving directory
COPY *.html /usr/share/nginx/html/

# Copy any additional static assets if they exist (CSS, JS, images)
# COPY *.css /usr/share/nginx/html/
# COPY *.js /usr/share/nginx/html/
# COPY assets/ /usr/share/nginx/html/assets/

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]
