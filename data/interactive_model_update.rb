
def perform
  dragons = "Adult Black Dragon, Adult Blue Dracolich, Adult Blue Dragon, Adult Brass Dragon, Adult Bronze Dragon, Adult Copper Dragon, Adult Gold Dragon, Adult Green Dragon, Adult Red Dragon, Adult Silver Dragon, Adult White Dragon, Ancient Black Dragon, Ancient Blue Dragon, Ancient Brass Dragon, Ancient Bronze Dragon, Ancient Copper Dragon, Ancient Gold Dragon, Ancient Green Dragon, Ancient Red Dragon, Ancient Silver Dragon, Ancient White Dragon, Black Dragon Wyrmling, Blue Dragon Wyrmling, Brass Dragon Wyrmling, Bronze Dragon Wyrmling, Copper Dragon Wyrmling, Gold Dragon Wyrmling, Green Dragon Wyrmling, Red Dragon Wyrmling, Silver Dragon Wyrmling, White Dragon Wyrmling"

  fs = open('interactive_model.txt', 'w')

  dragons.split(",").each do |dragon|
    entry = "{
          \"id\": null,
          \"name\": {
            \"value\": \"#{dragon.strip}\",
            \"synonyms\": []
          }
        },"
    fs.puts entry
  end

  fs.close
end

perform
