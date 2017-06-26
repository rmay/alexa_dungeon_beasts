require 'aws-sdk'
require 'sqlite3'
require 'pp'

def get_dynamo_conn
  #Aws::DynamoDB::Client.new(region: 'us-east-1')
  Aws::DynamoDB::Client.new(endpoint: 'http://localhost:8000')
end

def get_dynamodb_conn
  #Aws::DynamoDB::Resource.new(region: 'us-east-1')
  Aws::DynamoDB::Resource.new(endpoint: 'http://localhost:8000')
end

def setup_table
  attribute_defs = [
    { attribute_name: 'name', attribute_type: 'S' },
    { attribute_name: 'cr',   attribute_type: 'S' },
  ]

  key_schema = [
    { attribute_name: 'name', key_type: 'HASH' }
  ]

  index_schema = [
    { attribute_name: 'name', key_type: 'HASH'  },
    { attribute_name: 'cr',  key_type: 'RANGE' }
  ]

  global_indexes = [{
    index_name:             'namecrindex',
    key_schema:             index_schema,
    projection:             { projection_type: 'ALL' },
    provisioned_throughput: { read_capacity_units: 10, write_capacity_units: 10 }
  }]

  request = {
    attribute_definitions:    attribute_defs,
    table_name:               'Bestiary',
    key_schema:               key_schema,
    global_secondary_indexes: global_indexes,
    provisioned_throughput:   { read_capacity_units: 10, write_capacity_units: 10 }
  }
  begin
    dynamodb_client = get_dynamo_conn

    dynamodb_client.create_table(request)
    dynamodb_client.wait_until(:table_exists, table_name: 'Bestiary')
  rescue => e
    puts e
  end
end

def setup_sources_table
  attribute_defs = [
    { attribute_name: 'name', attribute_type: 'S' },
  ]

  key_schema = [
    { attribute_name: 'name', key_type: 'HASH' }
  ]

  index_schema = [
    { attribute_name: 'name', key_type: 'HASH'  },
  ]

  global_indexes = [{
    index_name:             'nameindex',
    key_schema:             index_schema,
    projection:             { projection_type: 'ALL' },
    provisioned_throughput: { read_capacity_units: 10, write_capacity_units: 10 }
  }]

  request = {
    attribute_definitions:    attribute_defs,
    table_name:               'Bestiary_sources',
    key_schema:               key_schema,
    global_secondary_indexes: global_indexes,
    provisioned_throughput:   { read_capacity_units: 10, write_capacity_units: 10 }
  }
  begin
    dynamodb_client = get_dynamo_conn

    dynamodb_client.create_table(request)
    dynamodb_client.wait_until(:table_exists, table_name: 'Bestiary_sources')
  rescue => e
    puts e
  end
end

def setup_beast_group_names_table
  attribute_defs = [
    { attribute_name: 'group_name', attribute_type: 'S' },
    { attribute_name: 'beasts', attribute_type: 'S' },
  ]

  #key_schema = [
  #  { attribute_name: 'name', key_type: 'RANGE' }
  #]

  key_schema = [
      {
        attribute_name: "group_name",
        key_type: "HASH",
      },
      {
        attribute_name: "beasts",
        key_type: "RANGE",
      },
  ]

  group_name_index_schema = [
    { attribute_name: 'group_name', key_type: 'HASH'  },
    { attribute_name: 'beasts', key_type: 'RANGE'  }
  ]

  global_indexes = [{
    index_name:             'group_name_index',
    key_schema:             group_name_index_schema,
    projection:             { projection_type: 'ALL' },
    provisioned_throughput: { read_capacity_units: 10, write_capacity_units: 10 }
  }
  ]

  request = {
    attribute_definitions:    attribute_defs,
    table_name:               'Bestiary_names',
    key_schema:               key_schema,
    global_secondary_indexes: global_indexes,
    provisioned_throughput:   { read_capacity_units: 10, write_capacity_units: 10 }
  }
  begin
    dynamodb_client = get_dynamo_conn

    dynamodb_client.create_table(request)
    dynamodb_client.wait_until(:table_exists, table_name: 'Bestiary_names')
  rescue => e
    puts e
  end
end

def select_sources_from_sqlite3_and_populate_dynamo
  db = SQLite3::Database.open("bestiary.db")
  db.results_as_hash = true
  db.execute("select * from sources") do |row|
    populate_sources_table(capitalize_words(row['name']))
  end
end

def populate_sources_table(name)
  dynamoDB = get_dynamodb_conn
  table = dynamoDB.table('Bestiary_sources')
  table.put_item({
    item:
      {
        name: name
  }})
end

def select_beasts_from_sqlite3_and_populate_dynamo
  db = SQLite3::Database.open("bestiary.db")
  db.results_as_hash = true
  db.execute("select * from beasts") do |row|
    traits = get_extra(db, "traits", row["ID"])
    actions = get_extra(db, "actions", row["ID"])
    legendaries = get_extra(db, "legendaries", row["ID"])
    beast_info = {name:               capitalize_words(row['name']),
                  size:               row['size'],
                  type:               row['type'],
                  alignment:          row['alignment'],
                  ac:                 row['ac'],
                  hp:                 row['hp'],
                  speed:              row['speed'],
                  str:                row['str'],
                  dex:                row['dex'],
                  con:                row['con'],
                  int:                row['int'],
                  wis:                row['wis'],
                  cha:                row['cha'],
                  skill:              row['skill'],
                  passive:            row['passive'],
                  resist:             row['resist'],
                  vulnerable:         row['vulnerable'],
                  immune:             row['immune'],
                  condition_immune:   row['condition_immune'],
                  senses:             row['senses'],
                  languages:          row['languages'],
                  cr:                 row['cr'],
                  traits:             traits,
                  actions:            actions,
                  legendaries:        legendaries,
                  source:             row['source'] }

    #puts beast_info
    populate_table(beast_info)
  end
end

def populate_table(beast_info)
  dynamoDB = get_dynamodb_conn
  table = dynamoDB.table('Bestiary')
  table.put_item({
    item:
      {
        name:             beast_info[:name],
        size:             beast_info[:size],
        type:             beast_info[:type],
        alignment:        beast_info[:alignment],
        ac:               beast_info[:ac],
        hp:               beast_info[:hp],
        speed:            beast_info[:speed],
        str:              beast_info[:str],
        dex:              beast_info[:dex],
        con:              beast_info[:con],
        int:              beast_info[:int],
        wis:              beast_info[:wis],
        cha:              beast_info[:cha],
        skill:            beast_info[:skill],
        passive:          beast_info[:passive],
        resist:           beast_info[:resist],
        vulnerable:       beast_info[:vulnerable],
        immune:           beast_info[:immune],
        condition_immune: beast_info[:condition_immune],
        senses:           beast_info[:senses],
        languages:        beast_info[:languages],
        cr:               beast_info[:cr],
        traits:           beast_info[:traits],
        actions:          beast_info[:actions],
        legendaries:      beast_info[:legendaries],
        source:           beast_info[:source]
  }})
end

def get_extra(db, table, id)
  extra = []
  db.execute("select * from " + table + " where beast = ?", id) do |row|
    name = "EMPTY"
    text = ""
    name = row['name'] unless row['name'].nil?
    text = row['text'] unless row['text'].nil?
    if name != "EMPTY"
      extra << name + ": " + text
    end
  end
  return extra
end

def select_beast_group_names_from_json_file_and_populate_dynamo
  file_name = "beast_groups.json"
  file = File.read file_name
  data = JSON.parse(file)
  data.each do |datum|
      group_info = {group_name: datum["group_name"],
                    beasts:     datum["beasts"],
                    source:     datum["source"]}
      #pp group_info
      populate_beast_name_table(group_info)
  end

end

def populate_beast_name_table(group_info)
  dynamoDB = get_dynamodb_conn
  table = dynamoDB.table('Bestiary_names')
  table.put_item({
    item:
      {
        group_name: group_info[:group_name],
        beasts:     group_info[:beasts],
        source:     group_info[:source]
        }})
end

def capitalize_words(string)
  string.gsub(/\S+/, &:capitalize)
end

def perform
  puts "Setting up dynamo sources table"
  setup_sources_table()
  puts "Populating dynamo sources from sqlite"
  select_sources_from_sqlite3_and_populate_dynamo()

  puts "Setting up dynamo bestiary table"
  setup_table()
  puts "Populating dynamo bestiary from sqlite"
  select_beasts_from_sqlite3_and_populate_dynamo()

  puts "Setting up group beast names"
  setup_beast_group_names_table()
  puts "Populating dynamo bestiary group names from json"
  select_beast_group_names_from_json_file_and_populate_dynamo()

end

perform()
