CREATE TABLE stock_transactions(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  user_id INTEGER NOT NULL,
  symbol TEXT NOT NULL,
  operation_type TEXT NOT NULL,
  shares_amount INTEGER NOT NULL,
  price REAL NOT NULL,
  transacted  TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
