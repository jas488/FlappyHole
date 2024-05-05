import pygame, sys, os, math, binascii, webbrowser, struct, random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Load Sounds
sounds = {
	"point": pygame.mixer.Sound("assets/sounds/point.mp3"),
	"flap": pygame.mixer.Sound("assets/sounds/flap.mp3"),
	"hit": pygame.mixer.Sound("assets/sounds/hit.mp3"),
	"fall": pygame.mixer.Sound("assets/sounds/fall.mp3"),
	"hitnfall": pygame.mixer.Sound("assets/sounds/hitnfall.mp3"),
	"swoosh": pygame.mixer.Sound("assets/sounds/swoosh.mp3")
}

# Game States:
# 0 - Main Screen
# 1 - Get Ready
# 2 - Playing
# 3 - Game Over
# 4 - Paused
# 5 - Settings
game_state = 0

def write_bin_file(file: str, hex_data: str):
	# Convert string to data
	bin_data = binascii.unhexlify(hex_data.replace(' ', ''))

	# Write data to a file
	with open(file, "wb") as f:
		f.write(bin_data)

def read_bin_file(file: str):
	# Read file
	with open(file, "rb") as f:
		bin_data = f.read()

	return binascii.hexlify(bin_data)

def reset_sett():
	write_bin_file('settings.dat', '53 45 54 54 00 00 48 49 00 00 00 00 4E 4D 00 53 46 58 00')

def reload_sett():
	global hi_score, night_mode, sfx
	
	result = read_bin_file('settings.dat')
	
	hi_score = int(result[16:24], 16)
	night_mode = bool(int(result[28:30]))
	sfx = bool(int(result[36:38]))

# sett.dat format:
# 53 45 54 54 00 00 48 49 00 00 00 00 4E 4D 00 53 46 58 00
# S  E  T  T  .  .  H  I  0  0  0  0  N  M  0  F  X  0
# Settings\00\00, HiScore 16x0000, Night Mode: False, SFX: False

# Max High Score: 2^32 - 1 (4 294 967 295)	

# Engine
class Engine():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.dt = 0 # Delta Time
		self.ct = 0 # Current Time
		self.time = 0
		self.a_state = 0
		
		self.is_running = True
		
		reload_sett()
	
	def create_window(self, width = 800, height = 600, title = "PyGame Engine Window", resizable = True):
		if resizable:
			window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
		else:
			window = pygame.display.set_mode((width, height))
		pygame.display.set_caption(title)
		
		return window    

	def update(self):
		self.dt = self.clock.tick(settings['max_fps'])
		self.ct = pygame.time.get_ticks()
		self.time = self.clock.get_time() / 1000
		
		if self.ct % ((1/5) * 1000) < self.dt:
			self.a_state += 1
		
		self.x_center = (pygame.display.get_surface().get_width() - win_params['width']) / 2
		self.y_center = (pygame.display.get_surface().get_height() - win_params['height']) / 2
	
	def renderer(self):
		pygame.display.flip()
		
	def handle_events(self):
		global game_state, night_mode, sfx
		
		for event in pygame.event.get():
			# Check if X clicked
			if event.type == pygame.QUIT:
				self.is_running = False
				
			if event.type == pygame.ACTIVEEVENT:
				if event.state == pygame.APPINPUTFOCUS and not event.gain:
					# Check if the window lost focus
					self.pause()
			
			# Check for KeyDown event    
			if event.type == pygame.KEYDOWN:
				
				# If space pressed start game if not started and flap if started
				if event.key == pygame.K_SPACE:
					if game_state == 2:
						#print("Jumped!")
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
					elif game_state == 1:
						game_state = 2
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
						game.flappy.rect.x = 128
						game.flappy.rect.y = 256
						
				# If ESC pressed, pause / unpause the game
				if event.key == pygame.K_ESCAPE:
					self.pause()
			
			# Check if mouse clicked
			if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
			   
				# If not touching pause button - flap, if touching - pause
				if not pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()): 
					if game_state == 2:
						#print("Jumped!")
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
					elif game_state == 1:
						game_state = 2
						game.flappy.y_vel = -6
						if sfx:
							pygame.mixer.Sound.play(sounds['flap'])
						game.flappy.mainscreen = False
						game.flappy.rect.x = 128
						game.flappy.rect.y = 256
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()) and game_state in [2, 4]:
						if game_state == 4:
							game_state = 0
						elif game_state == 2:
							game_state = 4
					
				elif pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					if game_state == 0:
						reload_sett()
						game_state = 5
					elif game_state == 5:
						game_state = 0
					
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 14, self.y_center + 256, 26, 28).collidepoint(pygame.mouse.get_pos()) and game_state == 4:
					self.pause()
						
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 - 24, 16, 16).collidepoint(pygame.mouse.get_pos()) and game_state == 5:
					if night_mode:
						night_mode = False
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {str(game.flappy.score.to_bytes(4, 'big')).replace('\\x', '').replace('b', '').replace('\'', '')} 4E 4D 00 53 46 58 {'0' + str(int(sfx))}')
					else:
						night_mode = True
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {str(game.flappy.score.to_bytes(4, 'big')).replace('\\x', '').replace('b', '').replace('\'', '')} 4E 4D 01 53 46 58 {'0' + str(int(sfx))}')
						
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 + 24, 16, 16).collidepoint(pygame.mouse.get_pos()) and game_state == 5:
					if sfx:
						sfx = False
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {str(game.flappy.score.to_bytes(4, 'big')).replace('\\x', '').replace('b', '').replace('\'', '')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 00')
					else:
						sfx = True
						write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {str(game.flappy.score.to_bytes(4, 'big')).replace('\\x', '').replace('b', '').replace('\'', '')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 01')
						
				if pygame.Rect(eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()) and game_state == 0:
					webbrowser.open('https://jas488.itch.io/flappy-hole')
				

				# This was meant to be a whole sharing feature, but it was too complicated and
				# addtitionally when i compiled the code to an exe, than antivirus kicks in, and
				# says that it's a spyware, cause it makes operations on file or smth like that so....
				# I'm not doin' this. If you get it to work, I'll apricieate that if you'll post it.
				'''if pygame.Rect(eng.x_center + win_params['width'] // 2 - 40, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
					share_img_surface = pygame.Surface((96, 116))
					if game.flappy.score > hi_score:
						share_img_surface.blit(eng.imgload("assets/textures/new_best.png"), (0, 0))
					else:
						share_img_surface.blit(eng.imgload("assets/textures/score.png"), (0, 0))
			
					game.render_score(share_img_surface, game.flappy.score, 32, True)
					game.render_score(share_img_surface, max(hi_score, game.flappy.score), 74, True)
					
					#pygame.scrap.put(pygame.SCRAP_BMP, )
					with open('test.bmp', 'wb') as f:
						data = pygame.image.tostring(share_img_surface, 'RGB')
						header = struct.pack('<2sIHHI', b'BM', len(data) + 54, 0, 0, 54)
						
						f.write(header + data)'''
					
	
	def pause(self):
		global game_state

		if game_state == 4:
			game_state = 2
		elif game_state == 2:
			game_state = 4
				
	def run(self):
		while self.is_running:
			self.handle_events()
			self.update()
			self.mainloop(window)
			game.flappy.update(score)
			self.renderer()
		pygame.quit()
		sys.exit()
	   
	def limg(self, path: str):
		return pygame.image.load(path)
	
	def resize(self, surface, size: tuple = (2, 2)):
		return pygame.transform.scale_by(surface, size)
	
	def crop(self, surface, size: tuple):
		return surface.subsurface(pygame.Rect(size[0], size[1], size[2], size[3]))
	
	def imgload(self, path: str, crop: tuple = False, resize_scale: tuple = (2, 2)):
		if crop != False:
			return self.resize(self.crop(self.limg(path), crop), resize_scale)
		else:
			return self.resize(self.limg(path), resize_scale)
	
	def mainloop(self, window):
		global game_state, night_mode, sfx

		game.update()
		game.render()
		
		# Check window size
		if window.get_width() < win_params['width'] or window.get_height() < win_params['height']:
			window = eng.create_window(max(win_params['width'], window.get_width()), max(win_params['height'], window.get_height()), win_params['title'], True)
		

		match game_state:
			case 0:
				window.blit(self.imgload('assets/textures/logo.png'), (self.x_center + win_params['width'] // 2 - 108, self.y_center + 128 + (6 * math.sin(eng.ct / 25 / 9))))
				window.blit(self.imgload('assets/textures/copyright.png'), (self.x_center + 4, self.y_center + win_params['height'] - 22))
			
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(self.imgload('assets/textures/buttons.png', (3 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(self.imgload('assets/textures/buttons.png', (3 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
			
				if not pygame.Rect(eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 70, 40, 14)), (eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 364))
				else:
					window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 70, 40, 13)), (eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 366))
					if pygame.mouse.get_pressed()[0]:
						game_state = 1
						game.pipe_x = 0
						game.flappy.rect.x = 128
						game.flappy.rect.y = 256
			
				if not pygame.Rect(eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
					#                                                              3 . 14
					window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 3 * 14, 40, 14)), (eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 364))
				else:
					window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 3 * 14, 40, 13)), (eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 366))
			case 1:
				window.blit(self.imgload('assets/textures/get_ready.png'), (self.x_center + win_params['width'] // 2 - 87, self.y_center + 205))
				window.blit(self.imgload('assets/textures/tutorial.png'), (self.x_center + win_params['width'] // 2 - 85, self.y_center + 296))
				
			case 2:
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(self.imgload('assets/textures/buttons.png', (0 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(self.imgload('assets/textures/buttons.png', (0 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
					
			case 4:
				# Darken the area
				dark = pygame.Surface((win_params['width'], win_params['height']))
				dark.fill((0, 0, 0))
				dark.set_alpha(64)
				window.blit(dark, (self.x_center, self. y_center))
			
				# Show "PAUSED" text
				window.blit(self.imgload('assets/textures/paused.png', False, (4, 4)), (self.x_center + win_params['width'] // 2 - 56, self.y_center + 180))
			
				if pygame.Rect(self.x_center + win_params['width'] // 2 - 14, self.y_center + 258, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(self.imgload('assets/textures/buttons.png', (1 * 13, 0, 13, 13)), (self.x_center + win_params['width'] // 2 - 14, self.y_center + 258))
				else:
					window.blit(self.imgload('assets/textures/buttons.png', (1 * 13, 0, 13, 14)), (self.x_center + win_params['width'] // 2 - 14, self.y_center + 256))
			
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(self.imgload('assets/textures/buttons.png', (2 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(self.imgload('assets/textures/buttons.png', (2 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
					
			case 5:
				if pygame.Rect(self.x_center + 12, self.y_center + 12, 26, 28).collidepoint(pygame.mouse.get_pos()):
					window.blit(self.imgload('assets/textures/buttons.png', (4 * 13, 0, 13, 13)), (self.x_center + 12, self.y_center + 14))
				else:
					window.blit(self.imgload('assets/textures/buttons.png', (4 * 13, 0, 13, 14)), (self.x_center + 12, self.y_center + 12))
					
				window.blit(eng.imgload('assets/textures/settings.png'), (self.x_center + win_params['width'] // 2 - 64, self.y_center + win_params['height'] // 2 - 58))
				
				if not night_mode:
					window.blit(eng.imgload('assets/textures/checkbox.png', (0, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 - 24))
				else:
					window.blit(eng.imgload('assets/textures/checkbox.png', (8, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 - 24))
				
				if not sfx:
					window.blit(eng.imgload('assets/textures/checkbox.png', (0, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 + 24))
				else:
					window.blit(eng.imgload('assets/textures/checkbox.png', (8, 0, 8, 8)), (self.x_center + win_params['width'] // 2 - 8, self.y_center + win_params['height'] // 2 + 24))
				
		

class Flappy(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		
		# Set Flappy image and position
		self.image = eng.imgload('assets/textures/flappy.png', (0, eng.a_state % 3 * 12, 17, 12))
		self.rect = self.image.get_rect()
		self.rect.x = 128
		self.rect.y = 256
		
		self.y_vel = 0 # Y Velocity
		
		self.ded_played = False
		
		self.gravity = -0.4
		
		self.score = 0
		self.dead = False
		
	def update(self, score):
		super().update()
		
		global game_state
		
		if game_state == 0:
			self.rect.x = 418
			self.rect.y = eng.y_center + 136 + (6 * math.sin(eng.ct / 25 / 9))

		if game_state == 2:
			self.image = eng.imgload('assets/textures/flappy.png', (0, eng.a_state % 3 * 12, 17, 12))
			
			self.y_vel -= self.gravity
			self.rect.y += self.y_vel
			
			if self.rect.y < 112:
				self.rect.y = 112
				self.y_vel = 0
		
		self. pipe_rect = pygame.Rect(eng.x_center + game.pipe_x + win_params['width'], eng.y_center + 370, 52, 52)
		self. pipe_mrect = pygame.Rect(eng.x_center + game.pipe_x + win_params['width'] + 25, eng.y_center + 370, 1, 52)

		if self.rect.y >= 370 and self.rect.colliderect(self.pipe_mrect):
			self.rect.y = 112
			self.score += 1
			if sfx:
				pygame.mixer.Sound.play(sounds['point'])
			
		if self.rect.colliderect(self.pipe_rect) and not self.rect.colliderect(self.pipe_mrect) or self.rect.y >= 376:
			while self.rect.colliderect(self.pipe_rect) and not self.rect.colliderect(self.pipe_mrect) or self.rect.y >= 376:
				self.rect.y -= 1
			game_state = 3
			if not self.ded_played:
				sounds['hit'].play()
				self.ded_played = True
		
		#print(str(round(eng.clock.get_fps() * 100) / 100) + " | " + str(round(self.y_vel * 10) / 10) + " | " + str(eng.a_state))

class GameSystem():
	def __init__(self, window):
		self.window = window
		self.bg_x = 0
		self.gnd_x = 0
		self.map_x = 0
		self.pipe_x = 0
		
		self.speed = 4
		self.flappy = Flappy()
	
	def update(self):
		if game_state == 2:
			self.bg_x -= 0.25 * self.speed
			self.pipe_x -= self.speed
		
		if game_state in [1, 2]:
			self.gnd_x -= self.speed
		
		if self.bg_x <= -288:
			self.bg_x = 0
			
		if self.gnd_x <= -308:
			self.gnd_x = 0
			
		if self.pipe_x <= -win_params['width'] - 52:
			self.pipe_x = 0 + random.randint(0, 24)

	def render(self):
		global game_state, hi_score, night_mode, sfx

		self.window.fill(settings['background'])
		
		# Draw Background
		for i in range(5):
			if not night_mode:
				self.window.blit(eng.imgload('assets/textures/backdrop.png'), (eng.x_center + (i * 288) + self.bg_x, eng.y_center))
			else:
				self.window.blit(eng.imgload('assets/textures/night_backdrop.png'), (eng.x_center + (i * 288) + self.bg_x, eng.y_center))
		
		# Draw Ground
		for i in range(4):
			self.window.blit(pygame.transform.flip(eng.imgload('assets/textures/ground.png'), False, True), (eng.x_center + (i * 308) + self.gnd_x, eng.y_center))
			self.window.blit(eng.imgload('assets/textures/ground.png'), (eng.x_center + i * 308 + self.gnd_x, eng.y_center + 400))
		
		# Draw Flappy
		if 0 <= game_state <= 4:
			self.window.blit(pygame.transform.rotate(self.flappy.image, -4 * self.flappy.y_vel), (self.flappy.rect.topleft[0] + eng.x_center, self.flappy.rect.topleft[1] + eng.y_center))

		# Draw Pipes
		self.window.blit(pygame.transform.flip(eng.imgload('assets/textures/pipe.png'), False, True), (eng.x_center + self.pipe_x + win_params['width'], eng.y_center))
		self.window.blit(eng.imgload('assets/textures/pipe.png'), (eng.x_center + self.pipe_x + win_params['width'], eng.y_center + 370))
		
		# Cover sides of window
		pygame.draw.rect(self.window, settings['background'], pygame.Rect(0, 0, eng.x_center, pygame.display.get_surface().get_height()))
		pygame.draw.rect(self.window, settings['background'], pygame.Rect(pygame.display.get_surface().get_width() - eng.x_center + 1, 0, eng.x_center, pygame.display.get_surface().get_height()))
	
		# Render score
		if game_state == 2:
			self.render_score(self.window, self.flappy.score)
		
		
		# If GameOver flag set to True, display "Game Over" text
		if game_state == 3:
			window.blit(eng.imgload("assets/textures/game_over.png"), (eng.x_center + win_params['width'] // 2 - 94, eng.y_center + 128))
			
			if self.flappy.score > hi_score:
				window.blit(eng.imgload("assets/textures/new_best.png"), (eng.x_center + win_params['width'] // 2 - 48, eng.y_center + 205))
				write_bin_file('settings.dat', f'53 45 54 54 00 00 48 49 {str(self.flappy.score.to_bytes(4, 'big')).replace('\\x', '').replace('b', '').replace('\'', '')} 4E 4D {'0' + str(int(night_mode))} 53 46 58 {'0' + str(int(sfx))}')
				#print(str(self.flappy.score.to_bytes(2, 'big')).replace('\\x', '').replace('b', '', 1).replace('\'', ''))
			else:
				window.blit(eng.imgload("assets/textures/score.png"), (eng.x_center + win_params['width'] // 2 - 48, eng.y_center + 205))
				
			self.render_score(self.window, self.flappy.score, 238, True)
			self.render_score(self.window, max(hi_score, self.flappy.score), 282, True)


			if not pygame.Rect(eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 332, 80, 28).collidepoint(pygame.mouse.get_pos()):
				window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 14, 40, 14)), (eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 332))
			else:
				if pygame.mouse.get_pressed()[0]:
					if sfx:
						sounds['swoosh'].play()
					self.flappy.rect.x = 128
					self.flappy.rect.y = 256
					self.flappy.ded_played = False
					self.flappy.score = 0
					self.bg_x = 0
					self.gnd_x = 0
					self.pipe_x = 0
					game_state = 1
					
					if self.flappy.score > hi_score:
						reload_sett()
						
				window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 14, 40, 13)), (eng.x_center + win_params['width'] // 2 - 84, eng.y_center + 334))
				

			if not pygame.Rect(eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 332, 80, 28).collidepoint(pygame.mouse.get_pos()):
				window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 0, 40, 14)), (eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 332))
			else:
				if pygame.mouse.get_pressed()[0]:
					game_state = 0
					self.flappy.score = 0
					self.flappy.ded_played = False
					self.pipe_x = 0
					if sfx:
						sounds['swoosh'].play()
				window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 0, 40, 13)), (eng.x_center + win_params['width'] // 2 + 4, eng.y_center + 334))
				

			# Look: 185 line
				
			#if not pygame.Rect(eng.x_center + win_params['width'] // 2 - 40, eng.y_center + 366, 80, 28).collidepoint(pygame.mouse.get_pos()):
			#	window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 56, 40, 14)), (eng.x_center + win_params['width'] // 2 - 40, eng.y_center + 364))
			#else:
			#	window.blit(eng.imgload('assets/textures/gui_buttons.png', (0, 56, 40, 13)), (eng.x_center + win_params['width'] // 2 - 40, eng.y_center + 366))

			#pygame.draw.line(self.window, (0, 255, 0), (eng.x_center + win_params['width'] // 2 - 94 + eng.imgload("assets/textures/game_over.png").get_width() // 2, 112), (eng.x_center + eng.x_center + win_params['width'] // 2 - 94 + eng.imgload("assets/textures/game_over.png").get_width() // 2, 180))
			#pygame.draw.line(self.window, (255, 0, 0), (320, 0), (320, 512))
		
	def render_score(self, surface, score: int, y: int = 128, small: bool = False, center = True):
		score_str = str(score)
		digit_width = 23
		total_width = len(score_str) * digit_width - 6
		
		x = (surface.get_width() - total_width) // 2
		
		for digit_str in score_str:
			digit = int(digit_str)
			if small:
				surface.blit(all_small_digits[digit], (eng.x_center + x, eng.y_center + y))
			else:
				surface.blit(all_digits[digit], (eng.x_center + x, eng.y_center + y))
			x += digit_width - (int(small) * 9)

eng = Engine()
win_params = {
	"width": 640,
	"height": 512,
	"title": "FlappyHole"
}
window = eng.create_window(win_params['width'], win_params['height'], win_params['title'], True)
pygame.display.set_icon(eng.imgload('assets/textures/icon.png'))

# Initialize scrap module
pygame.scrap.init()

game = GameSystem(window)

# Game Variables
score = 0

settings = {
	"max_fps": 30,
	"background": (48, 48, 48)
}

# Rendering
all_digits = [eng.imgload('assets/textures/digits.png', (n * 7, 0, 7, 10), (3, 3)) for n in range(10)]
all_small_digits = [eng.imgload('assets/textures/small_digits.png', (n * 6, 0, 6, 7), (3, 3)) for n in range(10)]

fpn = settings['max_fps'] / 6
game_tick = 0
cs = 0

eng.run()

	
# Get any digit: eng.imgload('assets/textures/digits.png', (n * 7, 0, 7, 10))
# Get any small digit: eng.imgload('assets/textures/small_digits.png', (n * 6, 0, 6, 7))
	
# Get any flappy: eng.imgload('assets/textures/flappy.png', (0, n * 12, 17, 12))

# Get any button: eng.imgload('assets/textures/gui_buttons.png', (0, n * 14, 40, 14))

# Get any checkbox: eng.imgload('assets/textures/checkbox.png', (0, n * 8, 8, 8))
