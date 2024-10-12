# Steam Market API scrapper

#### offer-scrapper-notifier todo:
- [ ] link parser
- [ ] database
- [ ] telegram notifier
- [ ] IP change per request
- [ ] External API for checking paint seed
- [ ] Steam API rate limit and anomaly detector

---
### postgres docker commands: 
```bash
docker pull postgre
docker run --name name -e POSTGRES_USER=passwd -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=dbname -p 5432:5432 -d postgres
```

### docker build command for custom windscribe-cli container
```bash
docker build -t offer_scrapper .
```
