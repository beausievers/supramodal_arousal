path = 'soundneg_output'
Dir.chdir(path)
all_files = Dir.glob("*.csv")

def check_answer(left_image, right_image, audio_file, selected_image_pos)
  soft_images = ['sad.png']
  hard_images = ['angry.png']

  # Were they supposed to match with hard or soft?
  target = (audio_file == 'clickemotionhard.wav') ? 'hard' : 'soft'

  images = [left_image, right_image]

  selection_index = (selected_image_pos == 'left') ? 0 : 1

  selected_image = images[selection_index]

  # Was their selection hard or soft?
  sel_soft = soft_images.include?(selected_image)

  puts "audio_file: #{audio_file}\t\t#{target}"
  puts "left_image: #{left_image}"
  puts "right_image: #{right_image}"
  puts "selected_image_pos: #{selected_image_pos}"
  puts "sel_soft: #{sel_soft}"

  congruent = sel_soft == (target == 'soft')

  puts "congruent: #{congruent}"

  return congruent
end

outfile = File.new('../soundneg.csv', 'w')
outfile.puts "id,shapes,audioFile,leftImage,rightImage,selectedImage,congruent,rt"
congruent_count = 0

all_files.each do |filename|
  f = File.new(filename, 'r')
  lines = f.readlines
  fields = lines[1].split(',')

  id = fields[0].strip
  shapes = fields[2].include?('01') ? 1 : 2
  congruent = check_answer(fields[2], fields[3], fields[4], fields[5]) ? 1 : 0
  left_image = fields[2]
  right_image = fields[3]
  audio_file = fields[4]
  selected_image = fields[5]
  rt = fields[6]

  congruent_count += 1 if congruent == 1

  out_string = "#{id},#{shapes},#{audio_file},#{left_image},#{right_image},#{selected_image},#{congruent},#{rt}"

  outfile.puts out_string
  puts out_string
  puts
end

puts "Congruent: #{congruent_count}"
puts "Total: #{all_files.count}"
