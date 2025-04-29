# solaris_conexus
## Setup web server
- Setup nextjs project:
``` $ npx create-next-app@latest solaris-frontend --typescript```
- Install nginx:
    + Setup `solaris` config in sites-available that fowards all traffic from `solaris.com` to frontend server
    + Create symbolic link to sites-enabled
    + Add `solaris.com` domain to localhost in `hosts` config.