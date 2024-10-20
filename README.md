# Steam Market API scrapper

#### offer-scrapper-notifier todo:
- [x] link parser
- [x] database
- [x] telegram notifier
- [x] IP change per request
- [x] API for checking paint seed
- [x] Steam API rate limit
- [x] Stability testing
- [x] code cleanup 
- [ ] better documentation / readme - what is this project etc...
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


### pip requirements
```bash
pip install psycopg2-binary
pip install requests[socks]
pip install python-telegram-bot
```



### docker commands:

Oczywiście, zamiast używać domyślnej tagu `latest`, możemy nadać bardziej precyzyjną nazwę dla commitów, np. `v1`. 

Oto, jak to wygląda:

### 1. **Commit kontenerów:**

Dla bazy danych PostgreSQL:
```bash
docker commit 061dd06d06d4 deagle_image:v1
```

Dla CSGOFloat:
```bash
docker commit 9ac6321619f8 csgofloat_image:v1
```

### 2. **Zapisz obrazy do plików tar:**

```bash
docker save -o deagle_image_v1.tar deagle_image:v1
docker save -o csgofloat_image_v1.tar csgofloat_image:v1
```

### 3. **Załaduj obrazy na nowym serwerze:**

```bash
docker load -i deagle_image_v1.tar
docker load -i csgofloat_image_v1.tar
```

### 4. **Uruchom kontenery:**

Dla PostgreSQL:
```bash
docker run --name name -e POSTGRES_USER=passwd -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=dbname -p 5432:5432 -d postgres
```

Dla CSGOFloat:
```bash
docker run --name csgofloat -v /host/config:/config -p 80:80 -p 443:443 -d csgofloat_image:v1
``` 

To pozwala na wersjonowanie i uniknięcie domyślnego użycia `latest`.



# how to run
1. start containers
2. init.db.py
3. check containers logs
