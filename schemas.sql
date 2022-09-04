CREATE TABLE trans_buy(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  user_id INTEGER NOT NULL,
  symbol TEXT NOT NULL,
  shares_amount INTEGER NOT NULL,
  price REAL NOT NULL,
  transacted  TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
