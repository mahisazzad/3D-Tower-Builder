from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# Game state variables
MENU_ACTIVE = True  # True when main menu is displayed
MENU_SELECTION = 0  # 0: Start, 1: Instructions, 2: Quit
SHOW_INSTRUCTIONS = False
menu_stars = []

GAME_ACTIVE = True
GAME_OVER = False
SCORE = 0
PERFECT_STREAK = 0
BLOCK_SPEED = 2.0
DIRECTION = 1  # 1 for right, -1 for left
MESSAGE = ""
MESSAGE_DURATION = 0
BLOCK_SIZE = 80  # Initial block size
CURRENT_LEVEL = 0
RESTART_TIME = 0
LIVES = 5  # Added lives system

# Tower blocks storage
tower_blocks = []  # Will store (x, z, width, depth, color) for each block
current_block = {"x": -300, "z": 0, "width": BLOCK_SIZE, "depth": BLOCK_SIZE, "color": (1, 0, 0)}

# Camera-related variables
camera_pos = (0, 500, 500)
camera_target = (0, 0, 0)
fovY = 60  # Field of view
GRID_LENGTH = 600  # Length of grid lines

# Visual effects
block_colors = [
    (1, 0, 0),      # Red
    (0, 1, 0),      # Green
    (0, 0, 1),      # Blue
    (1, 1, 0),      # Yellow
    (1, 0, 1),      # Magenta
    (0, 1, 1),      # Cyan
    (1, 0.5, 0),    # Orange
    (0.5, 0, 1),    # Purple
    (0, 0.5, 0.5)   # Teal
]

def draw_main_menu():
    glClearColor(0.05, 0.1, 0.2, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    update_menu_stars()
    draw_menu_stars()

    # Center the title
    title = "3D Tower Builder"
    font = GLUT_BITMAP_TIMES_ROMAN_24
    import ctypes
    title_bytes = title.encode("utf-8")
    title_array = (ctypes.c_ubyte * len(title_bytes))(*title_bytes)
    title_width = glutBitmapLength(font, title_array)
    title_x = 500 - title_width // 2
    title_y = 650

    glColor3f(1, 0.96, 0.8)
    draw_text(title_x, title_y, title, font)

    # Draw menu options as before
    options = ["Start Game", "Instructions", "Quit"]
    for i, option in enumerate(options):
        y = 500 - i * 60
        if i == MENU_SELECTION:
            glColor3f(1.0, 1.0, 0.0)  # Yellow
        else:
            glColor3f(1.0, 1.0, 1.0)  # White
        draw_text(400, y, option, GLUT_BITMAP_HELVETICA_18)
    glColor3f(1, 1, 1)  # Reset to default white

    glutSwapBuffers()


def generate_menu_stars(count=50):
    global menu_stars
    menu_stars = []
    for _ in range(count):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 800)
        speed = random.uniform(0.05, 0.15)  # Slow speed
        brightness = random.uniform(0.85, 1.0)
        menu_stars.append({"x": x, "y": y, "speed": speed, "brightness": brightness})

def update_menu_stars():
    for star in menu_stars:
        star["y"] -= star["speed"]
        if star["y"] < 0:
            star["x"] = random.uniform(0, 1000)
            star["y"] = 800
            star["speed"] = random.uniform(0.05, 0.15)
            star["brightness"] = random.uniform(0.85, 1.0)


def draw_menu_stars():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glPointSize(2)
    glBegin(GL_POINTS)
    for star in menu_stars:
        b = star["brightness"]
        glColor4f(b, b, b, b)
        glVertex2f(star["x"], star["y"])
    glEnd()
    glDisable(GL_BLEND)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)



def draw_instructions():
    glClearColor(0.05, 0.1, 0.2, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    draw_text(320, 600, "How to Play", GLUT_BITMAP_TIMES_ROMAN_24)
    instructions = [
        "Stack the blocks as high as you can!",
        "Click (left mouse) or press SPACE to drop a block.",
        "Align blocks perfectly for bonus points.",
        "You have 5 lives. Missing loses a life.",
        "Press 'R' to restart after Game Over.",
        "",
        "Press ENTER to return to menu."
    ]
    for i, line in enumerate(instructions):
        draw_text(220, 500 - i * 40, line, GLUT_BITMAP_HELVETICA_18)
    glutSwapBuffers()


# Background info and enhanced visuals
BACKGROUND_COLOR = (0.05, 0.1, 0.2)
stars = []  # Will store positions of stars in the background
clouds = []  # Will store cloud positions and sizes

# Particles for visual effects
particles = []  # Will store active particles

def generate_stars(count=300):
    """Generate random stars for the background"""
    global stars
    stars = []
    for _ in range(count):
        x = random.uniform(-1000, 1000)
        y = random.uniform(200, 2000)
        z = random.uniform(-1000, 1000)
        brightness = random.uniform(0.5, 1.0)
        size = random.uniform(1, 3)
        stars.append({"pos": (x, y, z), "brightness": brightness, "size": size})

def generate_clouds(count=10):
    """Generate cloud formations for the background"""
    global clouds
    clouds = []
    for _ in range(count):
        x = random.uniform(-1500, 1500)
        y = random.uniform(800, 1200)
        z = random.uniform(-1500, -800)
        size = random.uniform(100, 300)
        density = random.uniform(0.7, 0.9)
        clouds.append({"pos": (x, y, z), "size": size, "density": density})

def get_next_color():
    """Return a color for the next block based on current level"""
    return block_colors[CURRENT_LEVEL % len(block_colors)]

def reset_game():
    """Reset all game variables to start a new game"""
    global GAME_ACTIVE, GAME_OVER, SCORE, PERFECT_STREAK, BLOCK_SIZE, CURRENT_LEVEL, LIVES
    global tower_blocks, current_block, camera_pos, camera_target, MESSAGE

    GAME_ACTIVE = True
    GAME_OVER = False
    SCORE = 0
    PERFECT_STREAK = 0
    BLOCK_SIZE = 80
    CURRENT_LEVEL = 0
    LIVES = 5  # Reset lives
    
    # Reset tower blocks
    tower_blocks = []
    
    # Create the base block (doesn't move, is larger than player blocks)
    base_block = {"x": 0, "z": 0, "width": BLOCK_SIZE * 1.5, "depth": BLOCK_SIZE * 1.5, "color": (0.5, 0.5, 0.5)}
    tower_blocks.append(base_block)
    
    # Set up the first moving block
    current_block = {
        "x": -300, 
        "z": BLOCK_SIZE, 
        "width": BLOCK_SIZE, 
        "depth": BLOCK_SIZE, 
        "color": get_next_color()
    }
    
    # Reset camera
    camera_pos = (0, 500, 500)
    camera_target = (0, 0, 0)
    MESSAGE = "Stack the blocks! Click to drop. You have 5 lives!"
    
    # Generate background elements
    generate_stars()
    generate_clouds()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    # glColor3f(1, 1, 1)  # REMOVED or COMMENTED OUT
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800) # left, right, bottom, top
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_block(block, height=0):
    """Draw a single block with the specified properties"""
    glPushMatrix()
    glColor3f(*block["color"])
    
    # Position the block
    glTranslatef(block["x"], height, block["z"])
    
    # Calculate proportional height based on width
    # As blocks get narrower, they should get taller for better visualization
    height_scale = BLOCK_SIZE / max(block["width"], 20) * 0.8
    height_scale = min(height_scale, 3.0)  # Cap the maximum height
    
    # Draw the block as a scaled cube
    glScalef(block["width"]/60, BLOCK_SIZE/60 * height_scale, block["depth"]/60)  # Scale to match the block dimensions
    glutSolidCube(60)
    
    # Add a wireframe outline
    glColor3f(1, 1, 1)  # White wireframe
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glutWireCube(60.5)  # Slightly larger to avoid z-fighting
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glPopMatrix()

def draw_tower():
    """Draw all blocks in the tower"""
    # Draw base grid
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    
    # Draw grid lines
    spacing = 30
    extent = GRID_LENGTH
    for i in range(-extent, extent + 1, spacing):
        glVertex3f(i, 0, -extent)
        glVertex3f(i, 0, extent)
        glVertex3f(-extent, 0, i)
        glVertex3f(extent, 0, i)
    
    glEnd()
    glPopMatrix()
    
    # Draw tower blocks with accumulating height
    # Calculate true height of the base block for proper stacking
    base_block = tower_blocks[0]
    base_height = BLOCK_SIZE * (0.8 + (BLOCK_SIZE / max(base_block["width"], 20)) * 0.2)
    accumulated_height = base_height

    for i, block in enumerate(tower_blocks):
        # Calculate proportional height based on block width
        block_height = BLOCK_SIZE * (0.8 + (BLOCK_SIZE / max(block["width"], 20)) * 0.2)
        draw_block(block, accumulated_height)
        accumulated_height += block_height
    
    # Draw current moving block if game is active
    if GAME_ACTIVE and not GAME_OVER:
        draw_block(current_block, accumulated_height)

def add_particles(x, y, z, count=20, color=(1, 1, 0)):
    """Add particles for visual effects"""
    global particles
    for _ in range(count):
        velocity = [
            random.uniform(-2, 2),
            random.uniform(1, 5),
            random.uniform(-2, 2)
        ]
        lifetime = random.uniform(0.5, 1.5)
        size = random.uniform(1, 3)
        particles.append({
            "pos": [x, y, z],
            "velocity": velocity,
            "color": color,
            "lifetime": lifetime,
            "max_lifetime": lifetime,
            "size": size
        })

def update_particles():
    """Update particle positions and lifetimes"""
    global particles
    to_remove = []
    
    for i, particle in enumerate(particles):
        # Update position
        particle["pos"][0] += particle["velocity"][0]
        particle["pos"][1] += particle["velocity"][1]
        particle["pos"][2] += particle["velocity"][2]
        
        # Apply gravity
        particle["velocity"][1] -= 0.1
        
        # Decrease lifetime
        particle["lifetime"] -= 0.02
        if particle["lifetime"] <= 0:
            to_remove.append(i)
    
    # Remove dead particles
    for i in sorted(to_remove, reverse=True):
        if i < len(particles):
            particles.pop(i)

def draw_particles():
    """Draw all active particles"""
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glDepthMask(GL_FALSE)
    
    glBegin(GL_POINTS)
    for particle in particles:
        # Calculate alpha based on remaining lifetime
        alpha = particle["lifetime"] / particle["max_lifetime"]
        glColor4f(particle["color"][0], particle["color"][1], particle["color"][2], alpha)
        glVertex3f(particle["pos"][0], particle["pos"][1], particle["pos"][2])
    glEnd()
    
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def calculate_overlap():
    """Calculate the overlap between the current block and the top block of the tower"""
    if len(tower_blocks) == 0:
        return 1.0  # Safety fallback
    
    top_block = tower_blocks[-1]

    # Calculate overlap in X dimension
    left_current = current_block["x"] - current_block["width"]/2
    right_current = current_block["x"] + current_block["width"]/2
    left_top = top_block["x"] - top_block["width"]/2
    right_top = top_block["x"] + top_block["width"]/2

    # Calculate overlap range
    overlap_left = max(left_current, left_top)
    overlap_right = min(right_current, right_top)

    if overlap_right <= overlap_left:
        return 0  # No overlap

    overlap_width = overlap_right - overlap_left
    overlap_percent = overlap_width / current_block["width"]

    return overlap_percent

def trim_block(overlap_percent):
    """Trim the current block based on overlap and create a new block with appropriate size"""
    global current_block, BLOCK_SIZE
    
    if overlap_percent >= 0.99:
        # Perfect match, no trim needed
        new_width = tower_blocks[-1]["width"]
        new_block = {
            "x": tower_blocks[-1]["x"],  # Align with block below for perfect drops
            "z": current_block["z"],
            "width": new_width,
            "depth": current_block["depth"],
            "color": current_block["color"]
        }
        return new_block, True
    
    elif overlap_percent > 0:
        # Partial overlap, trim the block
        top_block = tower_blocks[-1]
        
        # Determine new width and position
        new_width = min(current_block["width"], top_block["width"]) * overlap_percent
        
        # Calculate the center position of the overlap
        left_current = current_block["x"] - current_block["width"]/2
        left_top = top_block["x"] - top_block["width"]/2
        overlap_left = max(left_current, left_top)
        new_center_x = overlap_left + new_width/2
        
        new_block = {
            "x": new_center_x,
            "z": current_block["z"],
            "width": new_width,
            "depth": current_block["depth"],
            "color": current_block["color"]
        }
        return new_block, False
    
    return None, False  # No overlap, game over

def drop_block():
    """Handle the block dropping logic"""
    global GAME_ACTIVE, GAME_OVER, SCORE, PERFECT_STREAK, MESSAGE, MESSAGE_DURATION, CURRENT_LEVEL, LIVES
    
    overlap_percent = calculate_overlap()
    
    # Add particles at the current block position for visual effect
    block_height = len(tower_blocks) * BLOCK_SIZE
    add_particles(current_block["x"], block_height, current_block["z"], 
                 color=current_block["color"])
    
    if overlap_percent > 0:
        trimmed_block, is_perfect = trim_block(overlap_percent)
        
        if trimmed_block:
            # Add the trimmed block to the tower
            tower_blocks.append(trimmed_block)
            
            # Update score
            SCORE += 1
            
            # Check if it was a perfect drop
            if is_perfect:
                PERFECT_STREAK += 1
                if PERFECT_STREAK >= 3:
                    SCORE += 5  # Bonus for 3+ perfect streak
                    MESSAGE = f"PERFECT STREAK! +5 BONUS!"
                    # Add more particles for the perfect streak
                    add_particles(trimmed_block["x"], block_height, trimmed_block["z"], 
                                 count=40, color=(1, 1, 0))
                else:
                    MESSAGE = "PERFECT!"
                    add_particles(trimmed_block["x"], block_height, trimmed_block["z"], 
                                 count=20, color=(0, 1, 0))
            else:
                PERFECT_STREAK = 0
                MESSAGE = f"Good! Overlap: {int(overlap_percent * 100)}%"
            
            MESSAGE_DURATION = time.time() + 1.5  # Show message for 1.5 seconds
            
            # Prepare the next block with potentially smaller size
            CURRENT_LEVEL += 1
            next_color = get_next_color()
            
            # Make the next block slightly smaller if not perfect
            next_width = trimmed_block["width"]
            if not is_perfect:
                next_width = max(next_width * 0.95, 20)  # Don't let it get too small
                
            # Create new moving block
            current_block["width"] = next_width
            current_block["depth"] = next_width
            current_block["x"] = -300  # Start from the left
            current_block["color"] = next_color
    else:
        # No overlap, lose a life
        LIVES -= 1
        MESSAGE = f"Missed! Lives remaining: {LIVES}"
        MESSAGE_DURATION = time.time() + 1.5
        
        if LIVES <= 0:
            # No more lives, game over
            GAME_OVER = True
            MESSAGE = f"GAME OVER! Final Score: {SCORE} - Press 'R' to restart"
            MESSAGE_DURATION = time.time() + 10  # Show message longer
        else:
            # Set up the next block with same size as last tower block
            current_block["width"] = tower_blocks[-1]["width"]
            current_block["depth"] = tower_blocks[-1]["depth"]
            current_block["x"] = -300  # Start from the left
            current_block["color"] = get_next_color()

def update_block_position():
    """Update the position of the current moving block"""
    global current_block, DIRECTION
    
    if GAME_ACTIVE and not GAME_OVER:
        # Update block position
        current_block["x"] += BLOCK_SPEED * DIRECTION
        
        # Reverse direction if block reaches boundaries
        if current_block["x"] > 300:
            DIRECTION = -1
        elif current_block["x"] < -300:
            DIRECTION = 1

def update_camera():
    """Update the camera position to follow the tower height"""
    global camera_pos, camera_target
    
    # Calculate total tower height with proportions
    tower_height = 0
    for block in tower_blocks:
        tower_height += BLOCK_SIZE * (0.8 + (BLOCK_SIZE / max(block["width"], 20)) * 0.2)
    
    # Only adjust camera when tower grows beyond a certain height
    if tower_height > 300:
        # Smoothly transition camera height
        target_y = tower_height - 100  # Camera height
        target_z = tower_height + 400  # Camera distance
        
        # Smoothly interpolate camera position
        current_y = camera_pos[1]
        current_z = camera_pos[2]
        
        # Simple linear interpolation
        camera_pos = (
            camera_pos[0],
            current_y + (target_y - current_y) * 0.1,
            current_z + (target_z - current_z) * 0.1
        )
        
        # Update camera target to look at top of tower
        camera_target = (0, tower_height - 100, 0)

def menu_keyboard_listener(key, x, y):
    global MENU_SELECTION, MENU_ACTIVE, SHOW_INSTRUCTIONS
    if SHOW_INSTRUCTIONS:
        if key == b'\r' or key == b'\n':  # Enter key
            SHOW_INSTRUCTIONS = False
            glutPostRedisplay()
        return

    if key == b'\r' or key == b'\n':  # Enter key
        if MENU_SELECTION == 0:
            # Start game
            MENU_ACTIVE = False
            reset_game()
            glutKeyboardFunc(keyboardListener)  # Switch to game controls
            glutPostRedisplay()
        elif MENU_SELECTION == 1:
            SHOW_INSTRUCTIONS = True
            glutPostRedisplay()
        elif MENU_SELECTION == 2:
            import sys, os
            os._exit(0)
    elif key == b'w' or key == b'W' or key == b'\x1b[A':  # Up arrow
        MENU_SELECTION = (MENU_SELECTION - 1) % 3
        glutPostRedisplay()
    elif key == b's' or key == b'S' or key == b'\x1b[B':  # Down arrow
        MENU_SELECTION = (MENU_SELECTION + 1) % 3
        glutPostRedisplay()


def keyboardListener(key, x, y):
    global GAME_ACTIVE, GAME_OVER, RESTART_TIME, MENU_ACTIVE
    # Space bar to drop block
    if key == b' ':
        if GAME_ACTIVE and not GAME_OVER:
            drop_block()
    
    # 'R' key to restart game
    elif key == b'r' or key == b'R':
        if GAME_OVER or not GAME_ACTIVE:
            if time.time() - RESTART_TIME > 0.5:
                reset_game()
                RESTART_TIME = time.time()
    
    # Escape key to return to menu
    elif key == b'\x1b':  # ESC key
        MENU_ACTIVE = True
        glutKeyboardFunc(menu_keyboard_listener)
        glutPostRedisplay()


def specialKeyListener(key, x, y):
    global camera_pos, BLOCK_SPEED, MENU_SELECTION
    if MENU_ACTIVE:  # Handle menu navigation
        if key == GLUT_KEY_UP:
            MENU_SELECTION = (MENU_SELECTION - 1) % 3
            glutPostRedisplay()
        elif key == GLUT_KEY_DOWN:
            MENU_SELECTION = (MENU_SELECTION + 1) % 3
            glutPostRedisplay()
    else:  # Game controls
        if key == GLUT_KEY_LEFT:
            camera_pos = (camera_pos[0] - 10, camera_pos[1], camera_pos[2])
        elif key == GLUT_KEY_RIGHT:
            camera_pos = (camera_pos[0] + 10, camera_pos[1], camera_pos[2])
        elif key == GLUT_KEY_UP:
            BLOCK_SPEED += 0.2
        elif key == GLUT_KEY_DOWN:
            BLOCK_SPEED = max(0.5, BLOCK_SPEED - 0.2)


def mouseListener(button, state, x, y):
    """Handle mouse inputs"""
    global GAME_ACTIVE, GAME_OVER
    
    # Left mouse button drops the block
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if GAME_ACTIVE and not GAME_OVER:
            drop_block()

def setupCamera():
    """Configure the camera's projection and view settings"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)  # Increased far clip distance
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Position the camera and set its orientation
    gluLookAt(
        camera_pos[0], camera_pos[1], camera_pos[2],  # Camera position
        camera_target[0], camera_target[1], camera_target[2],  # Look-at target
        0, 1, 0  # Up vector (y-axis)
    )

def idle():
    """Idle function for continuous updates"""
    if GAME_ACTIVE and not GAME_OVER:
        update_block_position()
        update_camera()
        update_particles()  # Update particle effects
    
    # Trigger screen redraw
    glutPostRedisplay()

def draw_star(x, y, z, brightness, size):
    """Draw a single star in the skybox"""
    glPointSize(size)
    glBegin(GL_POINTS)
    glColor4f(brightness, brightness, brightness, brightness)
    glVertex3f(x, y, z)
    glEnd()

def draw_cloud(x, y, z, size, density):
    """Draw a puffy cloud using multiple spheres"""
    glColor4f(1.0, 1.0, 1.0, density)  # White with transparency
    
    # Draw cloud as a collection of spheres
    cloud_parts = [
        {"offset": (0, 0, 0), "scale": 1.0},
        {"offset": (size*0.5, -size*0.1, 0), "scale": 0.7},
        {"offset": (-size*0.5, -size*0.1, 0), "scale": 0.7},
        {"offset": (0, -size*0.1, size*0.4), "scale": 0.6},
        {"offset": (0, -size*0.1, -size*0.4), "scale": 0.6},
    ]
    
    for part in cloud_parts:
        glPushMatrix()
        glTranslatef(
            x + part["offset"][0],
            y + part["offset"][1],
            z + part["offset"][2]
        )
        glScalef(size * part["scale"] * 0.01, size * part["scale"] * 0.01, size * part["scale"] * 0.01)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()

def draw_skybox():
    """Draw an enhanced skybox with stars and clouds"""
    glPushMatrix()
    
    # Increase size to encompass the entire scene
    size = 2000
    
    # Disable depth testing temporarily for the skybox
    glDepthMask(GL_FALSE)
    
    # Draw a gradient sky dome rather than a box
    glBegin(GL_TRIANGLE_FAN)
    
    # Center of dome at the top
    glColor3f(0.0, 0.1, 0.3)  # Dark blue at the top
    glVertex3f(0, size, 0)
    
    # Circle around the bottom
    segments = 32
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        x = math.cos(angle) * size
        z = math.sin(angle) * size
        
        # Gradient color from dark blue to lighter blue
        t = 0.5 * (1.0 + math.sin(angle))
        glColor3f(0.1 + t * 0.2, 0.2 + t * 0.3, 0.4 + t * 0.2)
        glVertex3f(x, 0, z)
    
    glEnd()
    
    # Draw stars
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    for star in stars:
        draw_star(star["pos"][0], star["pos"][1], star["pos"][2], 
                  star["brightness"], star["size"])
    
    # Draw clouds
    for cloud in clouds:
        draw_cloud(cloud["pos"][0], cloud["pos"][1], cloud["pos"][2], 
                   cloud["size"], cloud["density"])
    
    glDisable(GL_BLEND)
    
    # Restore depth testing
    glDepthMask(GL_TRUE)
    
    glPopMatrix()

def draw_hearts(x, y, count):
    """Draw hearts to represent remaining lives"""
    heart_width = 25
    spacing = 30
    
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    for i in range(count):
        heart_x = x + i * spacing
        
        # Draw a red heart using two circles and a triangle
        glColor3f(1.0, 0.0, 0.0)  # Red
        
        # Draw hearts using simpler method for OpenGL
        glBegin(GL_POLYGON)
        # Left half of heart
        for angle in range(0, 180, 30):
            rad_angle = math.radians(angle)
            px = heart_x - heart_width/4 + math.cos(rad_angle) * heart_width/4
            py = y + heart_width/4 + math.sin(rad_angle) * heart_width/4
            glVertex2f(px, py)
        
        # Right half of heart
        for angle in range(0, 180, 30):
            rad_angle = math.radians(angle)
            px = heart_x + heart_width/4 + math.cos(rad_angle) * heart_width/4
            py = y + heart_width/4 + math.sin(rad_angle) * heart_width/4
            glVertex2f(px, py)
        
        # Bottom point
        glVertex2f(heart_x, y - heart_width/3)
        glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_game_ui():
    """Draw game UI elements"""
    # Display score
    draw_text(10, 770, f"Score: {SCORE}")
    
    # Display lives
    draw_text(10, 740, f"Lives: ")
    draw_hearts(80, 740, LIVES)
    
    # Display streak if active
    if PERFECT_STREAK >= 2:
        draw_text(10, 710, f"Perfect Streak: {PERFECT_STREAK}")
    
    # Display level
    draw_text(10, 680, f"Level: {CURRENT_LEVEL + 1}")
    
    # Display message if active
    if time.time() < MESSAGE_DURATION:
        # Calculate size based on message content
        size = GLUT_BITMAP_HELVETICA_18
        if "PERFECT" in MESSAGE or "STREAK" in MESSAGE:
            size = GLUT_BITMAP_TIMES_ROMAN_24
        
        # Center the message
        msg_width = len(MESSAGE) * 9  # Approximate width
        x_pos = 500 - msg_width/2
        
        # Draw message with special coloring for special events
        if "PERFECT" in MESSAGE:
            glColor3f(1.0, 1.0, 0.0)  # Yellow for perfect
        elif "STREAK" in MESSAGE:
            glColor3f(1.0, 0.5, 0.0)  # Orange for streak
        elif "GAME OVER" in MESSAGE:
            glColor3f(1.0, 0.0, 0.0)  # Red for game over
        elif "Missed" in MESSAGE:
            glColor3f(1.0, 0.2, 0.2)  # Light red for missed blocks
        else:
            glColor3f(1.0, 1.0, 1.0)  # White for normal
            
        draw_text(x_pos, 400, MESSAGE, size)

def draw_effects():
    """Draw special effects like particles or visual enhancements"""
    # Draw particles
    draw_particles()

def showScreen():
    """Display function to render the game scene"""
    # Clear color and depth buffers
    glClearColor(*BACKGROUND_COLOR, 1.0)  # Dark blue background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Set up lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light 0 position and properties
    light_pos = [300, 500, 300, 1]  # Positional light
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    ambient = [0.3, 0.3, 0.3, 1.0]  # Increased ambient light for better visibility
    diffuse = [1.0, 1.0, 1.0, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    
    # Add a second light for better illumination
    glEnable(GL_LIGHT1)
    light1_pos = [-300, 300, -300, 1]
    light1_ambient = [0.1, 0.1, 0.2, 1.0]
    light1_diffuse = [0.4, 0.4, 0.6, 1.0]
    glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
    glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
    
    # Set material properties
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50)
    
    setupCamera()
    
    # Draw skybox first
    draw_skybox()
    
    # Draw all game elements
    draw_tower()
    
    # Draw special effects
    draw_effects()
    
    # Disable lighting for UI elements
    glDisable(GL_LIGHTING)
    
    # Draw UI elements
    draw_game_ui()
    
    # Swap buffers for smooth rendering
    glutSwapBuffers()

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# Game state variables
GAME_ACTIVE = True
GAME_OVER = False
SCORE = 0
PERFECT_STREAK = 0
BLOCK_SPEED = 2.0
DIRECTION = 1  # 1 for right, -1 for left
MESSAGE = ""
MESSAGE_DURATION = 0
BLOCK_SIZE = 80  # Initial block size
CURRENT_LEVEL = 0
RESTART_TIME = 0
LIVES = 5  # Added lives system

# Tower blocks storage
tower_blocks = []  # Will store (x, z, width, depth, color) for each block
current_block = {"x": -300, "z": 0, "width": BLOCK_SIZE, "depth": BLOCK_SIZE, "color": (1, 0, 0)}

# Camera-related variables
camera_pos = (0, 500, 500)
camera_target = (0, 0, 0)
fovY = 60  # Field of view
GRID_LENGTH = 600  # Length of grid lines

# Visual effects
block_colors = [
    (1, 0, 0),      # Red
    (0, 1, 0),      # Green
    (0, 0, 1),      # Blue
    (1, 1, 0),      # Yellow
    (1, 0, 1),      # Magenta
    (0, 1, 1),      # Cyan
    (1, 0.5, 0),    # Orange
    (0.5, 0, 1),    # Purple
    (0, 0.5, 0.5)   # Teal
]

# Background info and enhanced visuals
BACKGROUND_COLOR = (0.05, 0.1, 0.2)
stars = []  # Will store positions of stars in the background
clouds = []  # Will store cloud positions and sizes

# Particles for visual effects
particles = []  # Will store active particles

def generate_stars(count=300):
    """Generate random stars for the background"""
    global stars
    stars = []
    for _ in range(count):
        x = random.uniform(-1000, 1000)
        y = random.uniform(200, 2000)
        z = random.uniform(-1000, 1000)
        brightness = random.uniform(0.5, 1.0)
        size = random.uniform(1, 3)
        stars.append({"pos": (x, y, z), "brightness": brightness, "size": size})

def generate_clouds(count=10):
    """Generate cloud formations for the background"""
    global clouds
    clouds = []
    for _ in range(count):
        x = random.uniform(-1500, 1500)
        y = random.uniform(800, 1200)
        z = random.uniform(-1500, -800)
        size = random.uniform(100, 300)
        density = random.uniform(0.7, 0.9)
        clouds.append({"pos": (x, y, z), "size": size, "density": density})

def get_next_color():
    """Return a color for the next block based on current level"""
    return block_colors[CURRENT_LEVEL % len(block_colors)]

def reset_game():
    """Reset all game variables to start a new game"""
    global GAME_ACTIVE, GAME_OVER, SCORE, PERFECT_STREAK, BLOCK_SIZE, CURRENT_LEVEL, LIVES
    global tower_blocks, current_block, camera_pos, camera_target, MESSAGE

    GAME_ACTIVE = True
    GAME_OVER = False
    SCORE = 0
    PERFECT_STREAK = 0
    BLOCK_SIZE = 80
    CURRENT_LEVEL = 0
    LIVES = 5  # Reset lives
    
    # Reset tower blocks
    tower_blocks = []
    
    # Create the base block (doesn't move, is larger than player blocks)
    base_block = {"x": 0, "z": 0, "width": BLOCK_SIZE * 1.5, "depth": BLOCK_SIZE * 1.5, "color": (0.5, 0.5, 0.5)}
    # Position the first block above the base so it appears on screen
    current_block = {
        "x": -300,
        "z": BLOCK_SIZE,  # Same Z
        "width": BLOCK_SIZE,
        "depth": BLOCK_SIZE,
        "color": get_next_color()
    }

    tower_blocks.append(base_block)
    
    # Set up the first moving block
    current_block = {
        "x": -300, 
        "z": BLOCK_SIZE, 
        "width": BLOCK_SIZE, 
        "depth": BLOCK_SIZE, 
        "color": get_next_color()
    }
    
    # Reset camera
    camera_pos = (0, 400, 500)
    camera_target = (0, 0, 0)
    MESSAGE = "Stack the blocks! Click to drop. You have 5 lives!"
    
    # Generate background elements
    generate_stars()
    generate_clouds()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
 #   glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_block(block, height=0):
    """Draw a single block with the specified properties"""
    glPushMatrix()
    glColor3f(*block["color"])
    
    # Position the block
    glTranslatef(block["x"], height, block["z"])
    
    # Calculate proportional height based on width
    # As blocks get narrower, they should get taller for better visualization
    height_scale = BLOCK_SIZE / max(block["width"], 20) * 0.8
    height_scale = min(height_scale, 3.0)  # Cap the maximum height
    
    # Draw the block as a scaled cube
    glScalef(block["width"]/60, BLOCK_SIZE/60 * height_scale, block["depth"]/60)  # Scale to match the block dimensions
    glutSolidCube(60)
    
    # Add a wireframe outline
    glColor3f(1, 1, 1)  # White wireframe
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glutWireCube(60.5)  # Slightly larger to avoid z-fighting
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glPopMatrix()

def draw_tower():
    """Draw all blocks in the tower"""
    # Draw base grid
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    
    # Draw grid lines
    spacing = 30
    extent = GRID_LENGTH
    for i in range(-extent, extent + 1, spacing):
        glVertex3f(i, 0, -extent)
        glVertex3f(i, 0, extent)
        glVertex3f(-extent, 0, i)
        glVertex3f(extent, 0, i)
    
    glEnd()
    glPopMatrix()
    
    # Draw tower blocks with accumulating height
    accumulated_height = 0
    for i, block in enumerate(tower_blocks):
        # Calculate proportional height based on block width
        block_height = BLOCK_SIZE * (0.8 + (BLOCK_SIZE / max(block["width"], 20)) * 0.2)
        draw_block(block, accumulated_height)
        accumulated_height += block_height
    
    # Draw current moving block if game is active
    if GAME_ACTIVE and not GAME_OVER:
        draw_block(current_block, accumulated_height)

def add_particles(x, y, z, count=20, color=(1, 1, 0)):
    """Add particles for visual effects"""
    global particles
    for _ in range(count):
        velocity = [
            random.uniform(-2, 2),
            random.uniform(1, 5),
            random.uniform(-2, 2)
        ]
        lifetime = random.uniform(0.5, 1.5)
        size = random.uniform(1, 3)
        particles.append({
            "pos": [x, y, z],
            "velocity": velocity,
            "color": color,
            "lifetime": lifetime,
            "max_lifetime": lifetime,
            "size": size
        })

def update_particles():
    """Update particle positions and lifetimes"""
    global particles
    to_remove = []
    
    for i, particle in enumerate(particles):
        # Update position
        particle["pos"][0] += particle["velocity"][0]
        particle["pos"][1] += particle["velocity"][1]
        particle["pos"][2] += particle["velocity"][2]
        
        # Apply gravity
        particle["velocity"][1] -= 0.1
        
        # Decrease lifetime
        particle["lifetime"] -= 0.02
        if particle["lifetime"] <= 0:
            to_remove.append(i)
    
    # Remove dead particles
    for i in sorted(to_remove, reverse=True):
        if i < len(particles):
            particles.pop(i)

def draw_particles():
    """Draw all active particles"""
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glDepthMask(GL_FALSE)
    
    glBegin(GL_POINTS)
    for particle in particles:
        # Calculate alpha based on remaining lifetime
        alpha = particle["lifetime"] / particle["max_lifetime"]
        glColor4f(particle["color"][0], particle["color"][1], particle["color"][2], alpha)
        glVertex3f(particle["pos"][0], particle["pos"][1], particle["pos"][2])
    glEnd()
    
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def calculate_overlap():
    """Calculate the overlap between the current block and the top block of the tower"""
    if len(tower_blocks) == 1:
        return 1.0  # Consider first block perfect


    
    


    
    top_block = tower_blocks[-1 if len(tower_blocks) > 1 else 0]

    
    # Calculate overlap in X dimension
    left_current = current_block["x"] - current_block["width"]/2
    right_current = current_block["x"] + current_block["width"]/2
    left_top = top_block["x"] - top_block["width"]/2
    right_top = top_block["x"] + top_block["width"]/2
    
    # Calculate overlap
    overlap_left = max(left_current, left_top)
    overlap_right = min(right_current, right_top)
    
    if overlap_right <= overlap_left:
        return 0  # No overlap
        
    overlap_width = overlap_right - overlap_left
    overlap_percent = overlap_width / top_block["width"]
    

    
    return overlap_percent

def trim_block(overlap_percent):
    """Trim the current block based on overlap and create a new block with appropriate size"""
    global current_block, BLOCK_SIZE
    
    if overlap_percent >= 0.99:
        # Perfect match, no trim needed
        new_width = tower_blocks[-1]["width"]
        new_block = {
            "x": tower_blocks[-1]["x"],  # Align with block below for perfect drops
            "z": current_block["z"],
            "width": new_width,
            "depth": current_block["depth"],
            "color": current_block["color"]
        }
        return new_block, True
    
    elif overlap_percent > 0:
        # Partial overlap, trim the block
        top_block = tower_blocks[-1]
        
        # Determine new width and position
        new_width = min(current_block["width"], top_block["width"]) * overlap_percent
        
        # Calculate the center position of the overlap
        left_current = current_block["x"] - current_block["width"]/2
        left_top = top_block["x"] - top_block["width"]/2
        overlap_left = max(left_current, left_top)
        new_center_x = overlap_left + new_width/2
        
        new_block = {
            "x": new_center_x,
            "z": current_block["z"],
            "width": new_width,
            "depth": current_block["depth"],
            "color": current_block["color"]
        }
        return new_block, False
    
    return None, False  # No overlap, game over

def drop_block():
    """Handle the block dropping logic"""
    global GAME_ACTIVE, GAME_OVER, SCORE, PERFECT_STREAK, MESSAGE, MESSAGE_DURATION, CURRENT_LEVEL, LIVES
    
    overlap_percent = calculate_overlap()
    
    # Add particles at the current block position for visual effect
    block_height = len(tower_blocks) * BLOCK_SIZE
    add_particles(current_block["x"], block_height, current_block["z"], 
                 color=current_block["color"])
    
    if overlap_percent > 0:
        trimmed_block, is_perfect = trim_block(overlap_percent)
        
        if trimmed_block:
            # Add the trimmed block to the tower
            tower_blocks.append(trimmed_block)
            
            # Update score
            SCORE += 1
            
            # Check if it was a perfect drop
            if is_perfect:
                PERFECT_STREAK += 1
                if PERFECT_STREAK >= 3:
                    SCORE += 5  # Bonus for 3+ perfect streak
                    MESSAGE = f"PERFECT STREAK! +5 BONUS!"
                    # Add more particles for the perfect streak
                    add_particles(trimmed_block["x"], block_height, trimmed_block["z"], 
                                 count=40, color=(1, 1, 0))
                else:
                    MESSAGE = "PERFECT!"
                    add_particles(trimmed_block["x"], block_height, trimmed_block["z"], 
                                 count=20, color=(0, 1, 0))
            else:
                PERFECT_STREAK = 0
                MESSAGE = f"Good! Overlap: {int(overlap_percent * 100)}%"
            
            MESSAGE_DURATION = time.time() + 1.5  # Show message for 1.5 seconds
            
            # Prepare the next block with potentially smaller size
            CURRENT_LEVEL += 1
            # Power-Up every 10 levels
            if CURRENT_LEVEL != 1 and CURRENT_LEVEL % 10 == 0:
                MESSAGE = "POWER-UP! Auto Perfect Drop +10"
                SCORE += 10
                PERFECT_STREAK += 1
                trimmed_block = {
                    "x": tower_blocks[-1]["x"],
                    "z": current_block["z"],
                    "width": tower_blocks[-1]["width"],
                    "depth": tower_blocks[-1]["depth"],
                    "color": (1.0, 1.0, 0.6)  # Glowing yellow-white
                }
                tower_blocks.append(trimmed_block)
                MESSAGE_DURATION = time.time() + 1.5
                CURRENT_LEVEL += 1  # Extra level advance

            next_color = get_next_color()
            
            # Make the next block slightly smaller if not perfect
            next_width = trimmed_block["width"]
            if not is_perfect:
                next_width = max(next_width * 0.95, 20)  # Don't let it get too small
                
            # Create new moving block
            current_block["width"] = next_width
            current_block["depth"] = next_width
            current_block["x"] = -300  # Start from the left
            current_block["color"] = next_color
    else:
        # No overlap, lose a life
        LIVES -= 1
        MESSAGE = f"Missed! Lives remaining: {LIVES}"
        MESSAGE_DURATION = time.time() + 1.5
        
        if LIVES <= 0:
            # No more lives, game over
            GAME_OVER = True
            MESSAGE = f"GAME OVER! Final Score: {SCORE} - Press 'R' to restart"
            MESSAGE_DURATION = time.time() + 10  # Show message longer
        else:
            # Set up the next block with same size as last tower block
            current_block["width"] = tower_blocks[-1]["width"]
            current_block["depth"] = tower_blocks[-1]["depth"]
            current_block["x"] = -300  # Start from the left
            current_block["color"] = get_next_color()

def update_block_position():
    """Update the position of the current moving block"""
    global current_block, DIRECTION
    
    if GAME_ACTIVE and not GAME_OVER:
        # Update block position
        current_block["x"] += BLOCK_SPEED * DIRECTION
        
        # Reverse direction if block reaches boundaries
        if current_block["x"] > 300:
            DIRECTION = -1
        elif current_block["x"] < -300:
            DIRECTION = 1

def update_camera():
    """Update the camera position to follow the tower height"""
    global camera_pos, camera_target
    
    # Calculate total tower height with proportions
    tower_height = 0
    for block in tower_blocks:
        tower_height += BLOCK_SIZE * (0.8 + (BLOCK_SIZE / max(block["width"], 20)) * 0.2)
    
    # Only adjust camera when tower grows beyond a certain height
    if tower_height > 300:
        # Smoothly transition camera height
        target_y = tower_height - 100  # Camera height
        target_z = tower_height + 400  # Camera distance
        
        # Smoothly interpolate camera position
        current_y = camera_pos[1]
        current_z = camera_pos[2]
        
        # Simple linear interpolation
        camera_pos = (
            camera_pos[0],
            current_y + (target_y - current_y) * 0.1,
            current_z + (target_z - current_z) * 0.1
        )
        
        # Update camera target to look at top of tower
        camera_target = (0, tower_height - 100, 0)

def keyboardListener(key, x, y):
    """Handle keyboard inputs"""
    global GAME_ACTIVE, GAME_OVER, RESTART_TIME
    
    # Space bar to drop block
    if key == b' ':
        if GAME_ACTIVE and not GAME_OVER:
            drop_block()
    
    # 'R' key to restart game
    elif key == b'r' or key == b'R':
        if GAME_OVER or not GAME_ACTIVE:
            if time.time() - RESTART_TIME > 0.5:  # Prevent rapid restarts
                reset_game()
                RESTART_TIME = time.time()

def specialKeyListener(key, x, y):
    """Handle special key inputs (arrow keys)"""
    global camera_pos, BLOCK_SPEED
    
    # Arrow keys to adjust camera (debugging)
    if key == GLUT_KEY_LEFT:
        camera_pos = (camera_pos[0] - 10, camera_pos[1], camera_pos[2])
    elif key == GLUT_KEY_RIGHT:
        camera_pos = (camera_pos[0] + 10, camera_pos[1], camera_pos[2])
    elif key == GLUT_KEY_UP:
        BLOCK_SPEED += 0.2  # Increase speed
    elif key == GLUT_KEY_DOWN:
        BLOCK_SPEED = max(0.5, BLOCK_SPEED - 0.2)  # Decrease speed, minimum 0.5

def mouseListener(button, state, x, y):
    """Handle mouse inputs"""
    global GAME_ACTIVE, GAME_OVER
    
    # Left mouse button drops the block
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if GAME_ACTIVE and not GAME_OVER:
            drop_block()

def setupCamera():
    """Configure the camera's projection and view settings"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)  # Increased far clip distance
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Position the camera and set its orientation
    gluLookAt(
        camera_pos[0], camera_pos[1], camera_pos[2],  # Camera position
        camera_target[0], camera_target[1], camera_target[2],  # Look-at target
        0, 1, 0  # Up vector (y-axis)
    )

def idle():
    """Idle function for continuous updates"""
    if GAME_ACTIVE and not GAME_OVER:
        update_block_position()
        update_camera()
        update_particles()  # Update particle effects
    
    # Trigger screen redraw
    glutPostRedisplay()

def draw_star(x, y, z, brightness, size):
    """Draw a single star in the skybox"""
    glPointSize(size)
    glBegin(GL_POINTS)
    glColor4f(brightness, brightness, brightness, brightness)
    glVertex3f(x, y, z)
    glEnd()

def draw_cloud(x, y, z, size, density):
    """Draw a puffy cloud using multiple spheres"""
    glColor4f(1.0, 1.0, 1.0, density)  # White with transparency
    
    # Draw cloud as a collection of spheres
    cloud_parts = [
        {"offset": (0, 0, 0), "scale": 1.0},
        {"offset": (size*0.5, -size*0.1, 0), "scale": 0.7},
        {"offset": (-size*0.5, -size*0.1, 0), "scale": 0.7},
        {"offset": (0, -size*0.1, size*0.4), "scale": 0.6},
        {"offset": (0, -size*0.1, -size*0.4), "scale": 0.6},
    ]
    
    for part in cloud_parts:
        glPushMatrix()
        glTranslatef(
            x + part["offset"][0],
            y + part["offset"][1],
            z + part["offset"][2]
        )
        glScalef(size * part["scale"] * 0.01, size * part["scale"] * 0.01, size * part["scale"] * 0.01)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()

def draw_skybox():
    """Draw an enhanced skybox with stars and clouds"""
    glPushMatrix()
    
    # Increase size to encompass the entire scene
    size = 2000
    
    # Disable depth testing temporarily for the skybox
    glDepthMask(GL_FALSE)
    
    # Draw a gradient sky dome rather than a box
    glBegin(GL_TRIANGLE_FAN)
    
    # Center of dome at the top
    glColor3f(0.0, 0.1, 0.3)  # Dark blue at the top
    glVertex3f(0, size, 0)
    
    # Circle around the bottom
    segments = 32
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        x = math.cos(angle) * size
        z = math.sin(angle) * size
        
        # Gradient color from dark blue to lighter blue
        t = 0.5 * (1.0 + math.sin(angle))
        glColor3f(0.1 + t * 0.2, 0.2 + t * 0.3, 0.4 + t * 0.2)
        glVertex3f(x, 0, z)
    
    glEnd()
    
    # Draw stars
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    for star in stars:
        draw_star(star["pos"][0], star["pos"][1], star["pos"][2], 
                  star["brightness"], star["size"])
    
    # Draw clouds
    for cloud in clouds:
        draw_cloud(cloud["pos"][0], cloud["pos"][1], cloud["pos"][2], 
                   cloud["size"], cloud["density"])
    
    glDisable(GL_BLEND)
    
    # Restore depth testing
    glDepthMask(GL_TRUE)
    
    glPopMatrix()

def draw_hearts(x, y, count):
    """Draw hearts to represent remaining lives"""
    heart_width = 25
    spacing = 30
    
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    for i in range(count):
        heart_x = x + i * spacing
        
        # Draw a red heart using two circles and a triangle
        glColor3f(1.0, 0.0, 0.0)  # Red
        
        # Draw hearts using simpler method for OpenGL
        glBegin(GL_POLYGON)
        # Left half of heart
        for angle in range(0, 180, 30):
            rad_angle = math.radians(angle)
            px = heart_x - heart_width/4 + math.cos(rad_angle) * heart_width/4
            py = y + heart_width/4 + math.sin(rad_angle) * heart_width/4
            glVertex2f(px, py)
        
        # Right half of heart
        for angle in range(0, 180, 30):
            rad_angle = math.radians(angle)
            px = heart_x + heart_width/4 + math.cos(rad_angle) * heart_width/4
            py = y + heart_width/4 + math.sin(rad_angle) * heart_width/4
            glVertex2f(px, py)
        
        # Bottom point
        glVertex2f(heart_x, y - heart_width/3)
        glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_game_ui():
    """Draw game UI elements"""
    # Display score
    draw_text(10, 770, f"Score: {SCORE}")
    
    # Display lives
    draw_text(10, 740, f"Lives: ")
    draw_hearts(80, 740, LIVES)
    
    # Display streak if active
    if PERFECT_STREAK >= 2:
        draw_text(10, 710, f"Perfect Streak: {PERFECT_STREAK}")
    
    # Display level
    draw_text(10, 680, f"Level: {CURRENT_LEVEL + 1}")
    
    # Display message if active
    if time.time() < MESSAGE_DURATION:
        # Calculate size based on message content
        size = GLUT_BITMAP_HELVETICA_18
        if "PERFECT" in MESSAGE or "STREAK" in MESSAGE:
            size = GLUT_BITMAP_TIMES_ROMAN_24
        
        # Center the message
        msg_width = len(MESSAGE) * 9  # Approximate width
        x_pos = 500 - msg_width/2
        
        # Draw message with special coloring for special events
        if "PERFECT" in MESSAGE:
            glColor3f(1.0, 1.0, 0.0)  # Yellow for perfect
        elif "STREAK" in MESSAGE:
            glColor3f(1.0, 0.5, 0.0)  # Orange for streak
        elif "GAME OVER" in MESSAGE:
            glColor3f(1.0, 0.0, 0.0)  # Red for game over
        elif "Missed" in MESSAGE:
            glColor3f(1.0, 0.2, 0.2)  # Light red for missed blocks
        else:
            glColor3f(1.0, 1.0, 1.0)  # White for normal
            
        draw_text(x_pos, 400, MESSAGE, size)

def draw_effects():
    """Draw special effects like particles or visual enhancements"""
    # Draw particles
    draw_particles()

def showScreen():
    """Display function to render the game scene"""
    # Clear color and depth buffers
    glClearColor(*BACKGROUND_COLOR, 1.0)  # Dark blue background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Set up lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light 0 position and properties
    light_pos = [300, 500, 300, 1]  # Positional light
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    ambient = [0.3, 0.3, 0.3, 1.0]  # Increased ambient light for better visibility
    diffuse = [1.0, 1.0, 1.0, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    
    # Add a second light for better illumination
    glEnable(GL_LIGHT1)
    light1_pos = [-300, 300, -300, 1]
    light1_ambient = [0.1, 0.1, 0.2, 1.0]
    light1_diffuse = [0.4, 0.4, 0.6, 1.0]
    glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
    glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
    
    # Set material properties
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50)
    
    setupCamera()
    
    # Draw skybox first
    draw_skybox()
    
    # Draw all game elements
    draw_tower()
    
    # Draw special effects
    draw_effects()
    
    # Disable lighting for UI elements
    glDisable(GL_LIGHTING)
    
    # Draw UI elements
    draw_game_ui()
    
    # Swap buffers for smooth rendering
    glutSwapBuffers()


def main_display():
    if MENU_ACTIVE:
        if SHOW_INSTRUCTIONS:
            draw_instructions()
        else:
            draw_main_menu()
    else:
        showScreen()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Tower Builder - 5 Lives")
    glutDisplayFunc(main_display)
    glutKeyboardFunc(menu_keyboard_listener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glEnable(GL_POINT_SMOOTH)
    reset_game()
    generate_menu_stars()  # <--- ADD THIS LINE
    glutMainLoop()



if __name__ == "__main__":
    main()
    