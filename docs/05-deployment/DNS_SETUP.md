# DNS Setup (GoDaddy)

## Subdomain: bostonpayroll.adamlozo.com

### Step 1: Get Render URL

After deploying, your Render URL will be something like:
```
boston-payroll.onrender.com
```

### Step 2: Add CNAME in GoDaddy

1. Log into GoDaddy → My Products → Domain: `adamlozo.com`
2. Click "DNS"
3. Click "Add" under Records

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `bostonpayroll` |
| Value | `boston-payroll.onrender.com` |
| TTL | 1 Hour |

4. Click "Save"

### Step 3: Add Custom Domain in Render

1. Render Dashboard → boston-payroll → Settings
2. Scroll to "Custom Domains"
3. Click "Add Custom Domain"
4. Enter: `bostonpayroll.adamlozo.com`
5. Render will verify DNS (may take 5-30 min)

### Step 4: Verify SSL

Render auto-provisions SSL via Let's Encrypt.

1. Wait ~10 minutes after DNS propagation
2. Visit `https://bostonpayroll.adamlozo.com`
3. Verify padlock icon in browser

### Troubleshooting

**DNS not propagating?**
```bash
# Check DNS resolution
nslookup bostonpayroll.adamlozo.com

# Should return:
# bostonpayroll.adamlozo.com canonical name = boston-payroll.onrender.com
```

**SSL certificate error?**
- Wait 15-30 minutes
- Check Render dashboard for certificate status
- Ensure CNAME is correct (no trailing dot)

## Existing DNS Records (Reference)

Your other Boston dashboards likely have:
- `bostonbuilding.adamlozo.com` → building permits
- `bostonrestaurants.adamlozo.com` → restaurant inspections

This follows the same pattern.
