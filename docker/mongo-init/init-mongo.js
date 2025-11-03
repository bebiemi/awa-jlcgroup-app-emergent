// Script d'initialisation MongoDB
db = db.getSiblingDB('jlc_db');

// Création d'un utilisateur pour l'application
db.createUser({
  user: 'jlc_user',
  pwd: 'jlc_password',
  roles: [
    {
      role: 'readWrite',
      db: 'jlc_db'
    }
  ]
});

// Base de données d'authentification
db = db.getSiblingDB('auth_db');

db.createUser({
  user: 'auth_user',
  pwd: 'auth_password',
  roles: [
    {
      role: 'readWrite',
      db: 'auth_db'
    }
  ]
});

print('Databases and users created successfully');
