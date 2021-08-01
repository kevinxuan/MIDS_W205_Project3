# default endpoint
docker-compose exec mids ab -n 10 -H "Host: user1.comcast.com" http://localhost:5000/

# get_paid for user abc and xyz
docker-compose exec mids ab -n 3 -H "Host: user2.comcast.com" http://localhost:5000/get_paid\?user=abc\&amount=40
docker-compose exec mids ab -n 3 -H "Host: user1.comcast.com" http://localhost:5000/get_paid\?user=xyz\&amount=30

# purchase swords
docker-compose exec mids ab -n 2 -H "Host: server3.comcast.com" http://localhost:5000/purchase_a_sword\?user=xyz\&type=silver
docker-compose exec mids ab -n 1 -H "Host: server2.comcast.com" http://localhost:5000/purchase_a_sword\?user=xyz\&type=gold
docker-compose exec mids ab -n 3 -H "Host: server2.comcast.com" http://localhost:5000/purchase_a_sword\?user=abc\&type=bronze

# join guild
docker-compose exec mids ab -n 1 -H "Host: user1.comcast.com" http://localhost:5000/join_a_guild\?user=xyz\&name=best-guild
docker-compose exec mids ab -n 1 -H "Host: user1.comcast.com" http://localhost:5000/join_a_guild\?user=xyz\&name=another-guild
docker-compose exec mids ab -n 1 -H "Host: user2.comcast.com" http://localhost:5000/join_a_guild\?user=abc\&name=best-guild

# quit guild
docker-compose exec mids ab -n 1 -H "Host: facebook.com" http://localhost:5000/quit_guild\?user=xyz\&name=best-guild
