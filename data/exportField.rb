require 'sqlite3'

def get_beast_names
  db = SQLite3::Database.open "bestiary.db"
  #stm = db.prepare "SELECT name, source FROM beasts ORDER BY NAME"
  stm = db.prepare "SELECT name FROM beasts WHERE source = 'Monster Manual' ORDER BY NAME "
  rs = stm.execute

  #rs.each do |row|
  #  puts row.join "\s"
  #end

  return rs
end

def write_names(rs)
  open('beast_names3.txt', 'w') do |f|
    rs.each do |name|
      json_string = "{ \"name\": { \"value\": \"#{name.first}\"}},\n"
      puts json_string
      f.puts json_string
    end
  end
end

#get_beast_names

write_names(get_beast_names)
