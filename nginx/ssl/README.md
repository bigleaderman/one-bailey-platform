# SSL Certificate Setup

## Using Let's Encrypt (Certbot)

1. Install certbot on your VM:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. Get SSL certificate:
```bash
sudo certbot certonly --webroot -w /path/to/nginx/html \
  -d onebailey.shop -d www.onebailey.shop
```

3. Copy certificates to this directory:
```bash
sudo cp /etc/letsencrypt/live/onebailey.shop/fullchain.pem ./fullchain.pem
sudo cp /etc/letsencrypt/live/onebailey.shop/privkey.pem ./privkey.pem
sudo chmod 644 ./fullchain.pem
sudo chmod 600 ./privkey.pem
```

4. Set up auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Self-Signed Certificate (for testing)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=OneBailey/CN=onebailey.shop"
```

## Important Notes

- Never commit actual certificate files to git
- Certificates should be renewed every 90 days
- Keep private keys secure
