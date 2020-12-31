#Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 

import pygame
import random
from os import path

img_folder = path.join(path.dirname(__file__), 'Img')
snd_folder = path.join(path.dirname(__file__), 'Sounds')

HEIGHT = 600
WIDTH = 480
FPS = 60

#define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Shmup')
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')
def draw_text(surf,text,size, x, y):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x,y)
	surf.blit(text_surface, text_rect)

def draw_shield_bar(surf, x,y,pct):
	if pct < 0:
		pct = 0
	BAR_LENGTH = 100
	BAR_HEIGTH = 10
	fill = (pct/100) * BAR_LENGTH
	outline_rect = pygame.Rect(x,y,BAR_LENGTH, BAR_HEIGTH)
	fill_rect = pygame.Rect(x,y,fill,BAR_HEIGTH)
	pygame.draw.rect(surf, GREEN, fill_rect)
	pygame.draw.rect(surf, WHITE, outline_rect,2) #2=thick borders also makes emptyinside

def new_mob():
	m = Mob()
	all_sprites.add(m)
	mobs.add(m)

def draw_lives(surf, x,y, lives, img):
	for i in range(lives):
		img_rect = img.get_rect()
		img_rect.x = x + 30 * i
		img_rect.y = y
		surf.blit(img, img_rect)

def show_go_screen():
	window.fill(BLUE)
	window.blit(background, background_rect)
	draw_text(window, 'SHMUP!', 54, WIDTH / 2, HEIGHT / 4)
	draw_text(window, 'Arrow keys/WASD to move. Space to shoot', 22, WIDTH / 2, HEIGHT / 2)
	draw_text(window, 'Press a key to begin', 18, WIDTH / 2, HEIGHT * 3/4)
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False
				
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(player_img, (50,38))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.radius = 20
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.centerx = WIDTH / 2
		self.rect.bottom = HEIGHT - 10
		self.speedx = 0
		self.shield = 100
		self.shoot_delay = 250
		self.last_shot = pygame.time.get_ticks()
		self.lives = 3
		self.hidden = False
		self.hide_timer = pygame.time.get_ticks()
		self.power = 1
		self.power_time = pygame.time.get_ticks()
		self.power_time_limit = 5000

	def update(self):
		#timeout for powerup
		if self.power >= 2 and pygame.time.get_ticks() - self.power_time > self.power_time_limit:
			self.power -= 1
			self.power_time = pygame.time.get_ticks()


		#unhide if hidden
		if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
			self.hidden = False
			self.rect.centerx = WIDTH / 2
			self.rect.bottom = HEIGHT - 10

		self.speedx = 0
		keystate = pygame.key.get_pressed()
		if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
			self.speedx = -10
		if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
			self.speedx = 10
		if (keystate[pygame.K_RIGHT] or keystate[pygame.K_d]) and (keystate[pygame.K_LEFT] or keystate[pygame.K_a]):
			self.speedx = 0
		if self.rect.right > WIDTH:
			self.rect.right = WIDTH
		if self.rect.left < 0:
			self.rect.left = 0
		if keystate[pygame.K_SPACE]:
			self.shoot()
		self.rect.x += self.speedx

	def powerup(self):
		self.power += 1
		self.power_time = pygame.time.get_ticks() 


	def shoot(self):
		now = pygame.time.get_ticks()
		if now - self.last_shot > self.shoot_delay:
			self.last_shot = now
			if self.power == 1:
				shoot_snd.play()
				bullet = Bullet(self.rect.centerx, self.rect.top)
				all_sprites.add(bullet)
				bullets.add(bullet)
			if self.power >= 2:
				bullet1 = Bullet(self.rect.left, self.rect.centery)
				bullet2 = Bullet(self.rect.right, self.rect.centery)
				all_sprites.add(bullet1)
				all_sprites.add(bullet2)
				bullets.add(bullet1)
				bullets.add(bullet2)
				shoot_snd.play()

	def hide(self):
		self.hidden = True
		self.hide_timer = pygame.time.get_ticks()
		self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image_orig = random.choice(meteor_images)
		self.image_orig.set_colorkey(BLACK)
		self.image = self.image_orig.copy()
		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width * 0.85 / 2)
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-200,-self.rect.height)
		self.speedy = random.randrange(1,8)
		self.speedx = random.randrange(-3,3)
		self.rot = 0
		self.rot_speed = random.randrange(-8,8)
		self.last_update = pygame.time.get_ticks()


	def rotate(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > 50:
			self.last_update = now
			self.rot = (self.rot + self.rot_speed) % 360
			new_image = pygame.transform.rotate(self.image_orig, self.rot)
			old_center = self.rect.center
			self.image = new_image
			self.rect = self.image.get_rect()
			self.rect.center = old_center

	def update(self):
		self.rotate()
		self.rect.x += self.speedx
		self.rect.y += self.speedy
		if self.rect.top > HEIGHT + 10 or self.rect.right < -25 or self.rect.left > WIDTH + 20:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-200,-self.rect.height)
			self.speedy = random.randrange(1,8)
			self.speedx = random.randrange(-3,3)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = bullet_img
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = -10

	def update(self):
		self.rect.y += self.speedy
		if self.rect.bottom < -10:
			self.kill()

class Pow(pygame.sprite.Sprite):
	def __init__(self, center):
		pygame.sprite.Sprite.__init__(self)
		self.type = random.choice(['shield', 'gun'])
		self.image = powerup_img[self.type]
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.speedy = 5

	def update(self):
		self.rect.y += self.speedy
		if self.rect.top > HEIGHT + 10:
			self.kill()

class Explosion(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = explosion_anim[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 75

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.size][self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

#load all graphics
background = pygame.image.load(path.join(img_folder, 'Star Field.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_folder, 'playerShip1_orange.png')).convert()
player_mini_img = pygame.transform.scale(player_img,(25,19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_folder, 'laserRed16.png')).convert()

meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png','meteorBrown_med1.png',
				'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
				'meteorBrown_tiny1.png']
for img in meteor_list:
	meteor_images.append(pygame.image.load(path.join(img_folder, img)).convert())
 
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
	filename = f'regularExplosion0{i}.png'
	orig_img = pygame.image.load(path.join(img_folder, filename)).convert()
	orig_img.set_colorkey(BLACK)
	img = orig_img.copy()
	img_lg = pygame.transform.scale(img,(75,75))
	explosion_anim['lg'].append(img_lg)
	img = orig_img.copy()
	img_sm = pygame.transform.scale(img, (32,32))
	explosion_anim['sm'].append(img_sm)
	filename = f'sonicExplosion0{i}.png'
	img = pygame.image.load(path.join(img_folder, filename)).convert()
	img.set_colorkey(BLACK)
	explosion_anim['player'].append(img)
powerup_img = {}
powerup_img['shield'] = pygame.image.load(path.join(img_folder, 'shield.png')).convert()
powerup_img['gun'] = pygame.image.load(path.join(img_folder, 'gun.png')).convert()


#load game sounds
shoot_snd = pygame.mixer.Sound(path.join(snd_folder, 'Laser_Shoot.wav'))
explosion_snd = []
explosion_list = ['Explosion.wav', 'Explosion2.wav', 'Explosion3.wav']
for explosion in explosion_list:
	explosion_snd.append(pygame.mixer.Sound(path.join(snd_folder,explosion)))

player_death_snd = pygame.mixer.Sound(path.join(snd_folder, 'rumble1.ogg'))
gun_snd = pygame.mixer.Sound(path.join(snd_folder,'pow4.wav' ))
shield_snd = pygame.mixer.Sound(path.join(snd_folder, 'pow5.wav'))
pygame.mixer.music.load(path.join(snd_folder, 'StarMusic.ogg'))
pygame.mixer.music.set_volume(0.4)


pygame.mixer.music.play(loops=-1)

game_over = True
#game loop
running = True
while running:
	if game_over:
		show_go_screen()
		game_over = False
		all_sprites = pygame.sprite.Group()
		mobs = pygame.sprite.Group()
		bullets = pygame.sprite.Group()
		powerups = pygame.sprite.Group()
		player = Player()
		all_sprites.add(player)
		for i in range(8):
			new_mob()
		score = 0
	#running at right speed
	clock.tick(FPS)
	#process input(event)
	for event in pygame.event.get():	
		if event.type == pygame.QUIT:
			running = False

	#update
	all_sprites.update()

	#check if hit
	hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle) 
	for hit in hits:   #empty list==False
		player.shield -= hit.radius * 2
		expl = Explosion(hit.rect.center, 'sm')
		all_sprites.add(expl)
		new_mob()
		if player.shield <= 0:
			death_explosion = Explosion(player.rect.center, 'player')
			all_sprites.add(death_explosion)
			player_death_snd.play()
			player.hide()
			player.lives -= 1
			player.shield = 100


	#if player dies and the epxlosin has finished playing
	if player.lives == 0 and not death_explosion.alive():
		game_over = True
	#check if bullet hit a mob
	hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
	for hit in hits:
		score += 50 - hit.radius
		random.choice(explosion_snd).play()
		expl = Explosion(hit.rect.center, 'lg')
		all_sprites.add(expl)
		new_mob()
		if random.random() > 0.9:
			pow = Pow(hit.rect.center)
			all_sprites.add(pow)
			powerups.add(pow)

	#check if player hit powerup
	hits = pygame.sprite.spritecollide(player, powerups, True)
	for hit in hits:
		if hit.type == 'shield':
			player.shield += random.randrange(10,31)
			if player.shield >= 100:
				player.shield = 100
			shield_snd.play()
		if hit.type == 'gun':
			player.powerup()
			gun_snd.play()
	#draw/render
	window.fill(BLUE)
	window.blit(background, background_rect)
	all_sprites.draw(window)
	draw_text(window, str(score), 20, WIDTH/2, 10)
	draw_shield_bar(window, 5,5,player.shield)
	draw_lives(window, WIDTH - 100, 5, player.lives, player_mini_img)
	#after drawing everything
	pygame.display.flip()

pygame.quit()