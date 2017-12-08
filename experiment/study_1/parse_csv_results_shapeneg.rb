path = 'shapeneg_output'
Dir.chdir(path)
all_files = Dir.glob("*.csv")

def check_answer(left_image, audio_file, sel_sound)
  soft_images = ['bouba_01.png', 'bouba_02.png']
  hard_images = ['kiki_01.png', 'kiki_02.png']

  # What was the 1-2 mapping based on the selected sound?
  if audio_file == '1angry2sad.wav'
    hardnessarray = ['hard', 'soft']
  elsif audio_file == '1sad2angry.wav'
    hardnessarray = ['soft', 'hard']
  end

  # Was their selection hard or soft?
  hardness = hardnessarray[sel_sound.to_i - 1]

  # Was the image soft?
  imagesoft = soft_images.include?(left_image)
  puts "left_image: #{left_image}"
  puts "imagesoft: #{imagesoft}"
  puts "hardness sel: #{hardness}"

  congruent = imagesoft == (hardness == 'soft')

  puts "congruent: #{congruent}"

  return congruent
end

outfile = File.new('../shapeneg.csv', 'w')
outfile.puts "id,shapes,image,sound,sel_sound,congruent,rt"
congruent_count = 0

all_files.each do |filename|
  f = File.new(filename, 'r')
  lines = f.readlines
  fields = lines[1].split(',')

  id = fields[0].strip
  shapes = fields[2].include?('01') ? 1 : 2
  congruent = check_answer(fields[2], fields[3], fields[4]) ? 1 : 0
  image = fields[2]
  sound = fields[3]
  sel_sound = fields[4]
  rt = fields[5]

  congruent_count += 1 if congruent == 1

  out_string = "#{id},#{shapes},#{image},#{sound},#{sel_sound},#{congruent},#{rt}"

  outfile.puts out_string
  puts out_string
  puts
end

puts "Congruent: #{congruent_count}"
puts "Total: #{all_files.count}"
