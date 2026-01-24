"""
3D rendering engine using OpenGL for molecular visualization.

This module provides OpenGL-based 3D rendering capabilities for molecular
structures, including atom rendering as spheres, bond rendering as cylinders,
and camera/viewport management.
"""

import math
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field
from .models import Molecule, Atom, Bond, Point3D
from .molecule_3d import Molecule3D

try:
    import OpenGL.GL as gl
    import OpenGL.GLU as glu
    import OpenGL.GLUT as glut
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    # Create mock classes for when OpenGL is not available
    class MockGL:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    gl = MockGL()
    glu = MockGL()
    glut = MockGL()


@dataclass
class Camera3D:
    """
    3D camera for molecular visualization.
    
    Attributes:
        position: Camera position in 3D space
        target: Point the camera is looking at
        up: Up vector for camera orientation
        fov: Field of view in degrees
        near_plane: Near clipping plane distance
        far_plane: Far clipping plane distance
    """
    position: Point3D = field(default_factory=lambda: Point3D(0.0, 0.0, 10.0))
    target: Point3D = field(default_factory=lambda: Point3D(0.0, 0.0, 0.0))
    up: Point3D = field(default_factory=lambda: Point3D(0.0, 1.0, 0.0))
    fov: float = 45.0
    near_plane: float = 0.1
    far_plane: float = 100.0
    
    def get_distance_to_target(self) -> float:
        """Get the distance from camera to target."""
        return self.position.distance_to(self.target)
    
    def rotate_around_target(self, delta_x: float, delta_y: float) -> None:
        """
        Rotate camera around the target point.
        
        Args:
            delta_x: Horizontal rotation in degrees
            delta_y: Vertical rotation in degrees
        """
        # Convert to radians
        dx_rad = math.radians(delta_x)
        dy_rad = math.radians(delta_y)
        
        # Get current position relative to target
        rel_pos = Point3D(
            self.position.x - self.target.x,
            self.position.y - self.target.y,
            self.position.z - self.target.z
        )
        
        # Calculate spherical coordinates
        distance = math.sqrt(rel_pos.x**2 + rel_pos.y**2 + rel_pos.z**2)
        if distance == 0:
            return
        
        # Current angles
        theta = math.atan2(rel_pos.x, rel_pos.z)  # Horizontal angle
        phi = math.acos(rel_pos.y / distance)     # Vertical angle
        
        # Apply rotations
        theta += dx_rad
        phi += dy_rad
        
        # Clamp vertical angle to avoid flipping
        phi = max(0.1, min(math.pi - 0.1, phi))
        
        # Convert back to Cartesian coordinates
        new_rel_pos = Point3D(
            distance * math.sin(phi) * math.sin(theta),
            distance * math.cos(phi),
            distance * math.sin(phi) * math.cos(theta)
        )
        
        # Update camera position
        self.position = Point3D(
            self.target.x + new_rel_pos.x,
            self.target.y + new_rel_pos.y,
            self.target.z + new_rel_pos.z
        )
    
    def zoom(self, factor: float) -> None:
        """
        Zoom camera towards/away from target.
        
        Args:
            factor: Zoom factor (>1 zooms in, <1 zooms out)
        """
        # Get direction from target to camera
        direction = Point3D(
            self.position.x - self.target.x,
            self.position.y - self.target.y,
            self.position.z - self.target.z
        )
        
        # Scale the direction
        new_distance = self.get_distance_to_target() / factor
        
        # Clamp distance to reasonable bounds
        new_distance = max(0.5, min(50.0, new_distance))
        
        # Normalize direction and scale
        current_distance = self.get_distance_to_target()
        if current_distance > 0:
            scale = new_distance / current_distance
            self.position = Point3D(
                self.target.x + direction.x * scale,
                self.target.y + direction.y * scale,
                self.target.z + direction.z * scale
            )
    
    def reset_view(self, molecule_center: Point3D, molecule_size: float) -> None:
        """
        Reset camera to default view of the molecule.
        
        Args:
            molecule_center: Center point of the molecule
            molecule_size: Approximate size of the molecule
        """
        self.target = molecule_center
        
        # Position camera at a reasonable distance
        distance = max(10.0, molecule_size * 3.0)
        self.position = Point3D(
            molecule_center.x + distance * 0.7,
            molecule_center.y + distance * 0.5,
            molecule_center.z + distance * 0.7
        )
        
        self.up = Point3D(0.0, 1.0, 0.0)


@dataclass
class RenderSettings:
    """
    Settings for 3D molecular rendering.
    
    Attributes:
        atom_scale: Scale factor for atom spheres
        bond_radius: Radius of bond cylinders
        show_hydrogens: Whether to render hydrogen atoms
        use_element_colors: Whether to use element-specific colors
        background_color: Background color (R, G, B, A)
        lighting_enabled: Whether to enable lighting
        wireframe_mode: Whether to render in wireframe mode
    """
    atom_scale: float = 1.0
    bond_radius: float = 0.1
    show_hydrogens: bool = True
    use_element_colors: bool = True
    background_color: Tuple[float, float, float, float] = (0.1, 0.1, 0.1, 1.0)
    lighting_enabled: bool = True
    wireframe_mode: bool = False


class Renderer3D:
    """
    OpenGL-based 3D renderer for molecular structures.
    
    This class handles all 3D rendering operations including atom rendering
    as spheres, bond rendering as cylinders, and camera management.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the 3D renderer.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        if not OPENGL_AVAILABLE:
            print("Warning: OpenGL is not available. 3D rendering will be disabled.")
        
        self.width = width
        self.height = height
        self.camera = Camera3D()
        self.settings = RenderSettings()
        
        # Element colors (CPK coloring scheme)
        self.element_colors = {
            'H': (1.0, 1.0, 1.0),      # White
            'C': (0.3, 0.3, 0.3),      # Dark gray
            'N': (0.0, 0.0, 1.0),      # Blue
            'O': (1.0, 0.0, 0.0),      # Red
            'F': (0.0, 1.0, 0.0),      # Green
            'P': (1.0, 0.5, 0.0),      # Orange
            'S': (1.0, 1.0, 0.0),      # Yellow
            'Cl': (0.0, 1.0, 0.0),     # Green
            'Br': (0.5, 0.0, 0.0),     # Dark red
            'I': (0.5, 0.0, 0.5),      # Purple
        }
        
        # Van der Waals radii for atom sizing
        self.vdw_radii = {
            'H': 0.3, 'C': 0.7, 'N': 0.65, 'O': 0.6,
            'F': 0.5, 'P': 1.0, 'S': 1.0, 'Cl': 1.0,
            'Br': 1.2, 'I': 1.4
        }
        
        self._initialized = False
    
    def initialize_opengl(self) -> None:
        """Initialize OpenGL settings and context."""
        if not OPENGL_AVAILABLE or self._initialized:
            return
        
        # Enable depth testing
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        
        # Enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Set up lighting if enabled
        if self.settings.lighting_enabled:
            self._setup_lighting()
        
        # Set background color
        bg = self.settings.background_color
        gl.glClearColor(bg[0], bg[1], bg[2], bg[3])
        
        # Set viewport
        gl.glViewport(0, 0, self.width, self.height)
        
        self._initialized = True
    
    def _setup_lighting(self) -> None:
        """Set up OpenGL lighting."""
        if not OPENGL_AVAILABLE:
            return
            
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        
        # Light position (from camera direction)
        light_pos = [
            self.camera.position.x,
            self.camera.position.y,
            self.camera.position.z,
            1.0
        ]
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, light_pos)
        
        # Light properties
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        # Material properties
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 50.0)
        
        # Enable color material
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE)
    
    def set_viewport(self, width: int, height: int) -> None:
        """
        Set the viewport size.
        
        Args:
            width: New viewport width
            height: New viewport height
        """
        self.width = width
        self.height = height
        if OPENGL_AVAILABLE:
            gl.glViewport(0, 0, width, height)
    
    def set_camera_projection(self) -> None:
        """Set up the camera projection matrix."""
        if not OPENGL_AVAILABLE:
            return
            
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        aspect_ratio = self.width / self.height if self.height > 0 else 1.0
        glu.gluPerspective(
            self.camera.fov,
            aspect_ratio,
            self.camera.near_plane,
            self.camera.far_plane
        )
    
    def set_camera_view(self) -> None:
        """Set up the camera view matrix."""
        if not OPENGL_AVAILABLE:
            return
            
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        glu.gluLookAt(
            self.camera.position.x, self.camera.position.y, self.camera.position.z,
            self.camera.target.x, self.camera.target.y, self.camera.target.z,
            self.camera.up.x, self.camera.up.y, self.camera.up.z
        )
    
    def clear_screen(self) -> None:
        """Clear the screen and depth buffer."""
        if OPENGL_AVAILABLE:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    def render_molecule(self, molecule_3d: Molecule3D) -> None:
        """
        Render a 3D molecule.
        
        Args:
            molecule_3d: 3D molecule to render
        """
        if not OPENGL_AVAILABLE:
            print("OpenGL not available - cannot render 3D molecule")
            return
            
        if not self._initialized:
            self.initialize_opengl()
        
        # Set up camera
        self.set_camera_projection()
        self.set_camera_view()
        
        # Clear screen
        self.clear_screen()
        
        # Update lighting position
        if self.settings.lighting_enabled:
            self._setup_lighting()
        
        # Render atoms
        self._render_atoms(molecule_3d.molecule)
        
        # Render bonds
        self._render_bonds(molecule_3d.molecule)
    
    def _render_atoms(self, molecule: Molecule) -> None:
        """
        Render atoms as spheres.
        
        Args:
            molecule: Molecule containing atoms to render
        """
        if not OPENGL_AVAILABLE:
            return
            
        for atom in molecule.atoms:
            if not atom.position_3d:
                continue
            
            # Skip hydrogens if not showing them
            if not self.settings.show_hydrogens and atom.element.symbol == 'H':
                continue
            
            # Get atom color
            if self.settings.use_element_colors:
                color = self.element_colors.get(atom.element.symbol, (0.5, 0.5, 0.5))
            else:
                color = (0.7, 0.7, 0.7)
            
            # Get atom radius
            base_radius = self.vdw_radii.get(atom.element.symbol, 0.7)
            radius = base_radius * self.settings.atom_scale
            
            # Set color
            gl.glColor3f(color[0], color[1], color[2])
            
            # Render sphere
            self._render_sphere(atom.position_3d, radius)
    
    def _render_bonds(self, molecule: Molecule) -> None:
        """
        Render bonds as cylinders.
        
        Args:
            molecule: Molecule containing bonds to render
        """
        if not OPENGL_AVAILABLE:
            return
            
        for bond in molecule.bonds:
            if not bond.atom1.position_3d or not bond.atom2.position_3d:
                continue
            
            # Skip bonds to hydrogens if not showing them
            if not self.settings.show_hydrogens:
                if (bond.atom1.element.symbol == 'H' or 
                    bond.atom2.element.symbol == 'H'):
                    continue
            
            # Set bond color (gray for now)
            gl.glColor3f(0.5, 0.5, 0.5)
            
            # Render cylinder
            self._render_cylinder(
                bond.atom1.position_3d,
                bond.atom2.position_3d,
                self.settings.bond_radius
            )
    
    def _render_sphere(self, position: Point3D, radius: float, slices: int = 16, stacks: int = 16) -> None:
        """
        Render a sphere at the given position.
        
        Args:
            position: Center position of the sphere
            radius: Sphere radius
            slices: Number of longitude divisions
            stacks: Number of latitude divisions
        """
        if not OPENGL_AVAILABLE:
            return
            
        gl.glPushMatrix()
        gl.glTranslatef(position.x, position.y, position.z)
        
        if self.settings.wireframe_mode:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        
        # Use GLU quadric for sphere rendering
        quadric = glu.gluNewQuadric()
        glu.gluQuadricNormals(quadric, glu.GLU_SMOOTH)
        glu.gluSphere(quadric, radius, slices, stacks)
        glu.gluDeleteQuadric(quadric)
        
        gl.glPopMatrix()
    
    def _render_cylinder(self, start: Point3D, end: Point3D, radius: float, slices: int = 12) -> None:
        """
        Render a cylinder between two points.
        
        Args:
            start: Starting point of the cylinder
            end: Ending point of the cylinder
            radius: Cylinder radius
            slices: Number of radial divisions
        """
        if not OPENGL_AVAILABLE:
            return
            
        # Calculate cylinder direction and length
        direction = Point3D(end.x - start.x, end.y - start.y, end.z - start.z)
        length = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
        
        if length == 0:
            return
        
        # Normalize direction
        direction = Point3D(direction.x/length, direction.y/length, direction.z/length)
        
        gl.glPushMatrix()
        
        # Translate to start position
        gl.glTranslatef(start.x, start.y, start.z)
        
        # Calculate rotation to align with direction
        # Default cylinder is along Z-axis, we need to rotate to align with direction
        if abs(direction.z - 1.0) > 1e-6:  # Not already aligned with Z
            if abs(direction.z + 1.0) < 1e-6:  # Pointing in -Z direction
                gl.glRotatef(180.0, 1.0, 0.0, 0.0)
            else:
                # Calculate rotation axis (cross product of Z and direction)
                axis_x = -direction.y
                axis_y = direction.x
                axis_z = 0.0
                
                # Calculate rotation angle
                angle = math.degrees(math.acos(direction.z))
                
                if abs(axis_x) > 1e-6 or abs(axis_y) > 1e-6:
                    gl.glRotatef(angle, axis_x, axis_y, axis_z)
        
        if self.settings.wireframe_mode:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        
        # Render cylinder
        quadric = glu.gluNewQuadric()
        glu.gluQuadricNormals(quadric, glu.GLU_SMOOTH)
        glu.gluCylinder(quadric, radius, radius, length, slices, 1)
        glu.gluDeleteQuadric(quadric)
        
        gl.glPopMatrix()
    
    def handle_rotation(self, delta_x: float, delta_y: float) -> None:
        """
        Handle mouse rotation input.
        
        Args:
            delta_x: Horizontal mouse movement
            delta_y: Vertical mouse movement
        """
        # Convert pixel movement to rotation angles
        rotation_speed = 0.5
        self.camera.rotate_around_target(
            delta_x * rotation_speed,
            delta_y * rotation_speed
        )
    
    def handle_zoom(self, zoom_factor: float) -> None:
        """
        Handle zoom input.
        
        Args:
            zoom_factor: Zoom factor (>1 zooms in, <1 zooms out)
        """
        self.camera.zoom(zoom_factor)
    
    def reset_view(self, molecule_3d: Molecule3D) -> None:
        """
        Reset camera to default view of the molecule.
        
        Args:
            molecule_3d: Molecule to focus on
        """
        center = molecule_3d.get_center_of_mass()
        if not center:
            center = Point3D(0.0, 0.0, 0.0)
        
        bounding_box = molecule_3d.get_bounding_box()
        if bounding_box:
            min_pt, max_pt = bounding_box
            size = max(
                abs(max_pt.x - min_pt.x),
                abs(max_pt.y - min_pt.y),
                abs(max_pt.z - min_pt.z)
            )
        else:
            size = 5.0
        
        self.camera.reset_view(center, size)
    
    def export_image(self, filename: str, format: str = "PNG") -> bool:
        """
        Export the current rendered view as an image.
        
        Args:
            filename: Output filename
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            True if export was successful
        """
        if not OPENGL_AVAILABLE:
            print("OpenGL not available - cannot export image")
            return False
            
        try:
            # Read pixels from framebuffer
            gl.glReadBuffer(gl.GL_FRONT)
            pixels = gl.glReadPixels(0, 0, self.width, self.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
            
            # Convert to PIL Image and save
            try:
                from PIL import Image
                import numpy as np
                
                # Convert to numpy array and flip vertically (OpenGL has origin at bottom-left)
                image_array = np.frombuffer(pixels, dtype=np.uint8)
                image_array = image_array.reshape((self.height, self.width, 3))
                image_array = np.flipud(image_array)
                
                # Create PIL image and save
                image = Image.fromarray(image_array, 'RGB')
                image.save(filename, format)
                return True
                
            except ImportError:
                print("PIL (Pillow) is required for image export")
                return False
                
        except Exception as e:
            print(f"Error exporting image: {e}")
            return False
    
    def get_render_info(self) -> Dict[str, any]:
        """
        Get information about the current render state.
        
        Returns:
            Dictionary containing render information
        """
        return {
            'viewport_size': (self.width, self.height),
            'camera_position': (self.camera.position.x, self.camera.position.y, self.camera.position.z),
            'camera_target': (self.camera.target.x, self.camera.target.y, self.camera.target.z),
            'camera_distance': self.camera.get_distance_to_target(),
            'fov': self.camera.fov,
            'lighting_enabled': self.settings.lighting_enabled,
            'wireframe_mode': self.settings.wireframe_mode,
            'show_hydrogens': self.settings.show_hydrogens,
            'atom_scale': self.settings.atom_scale,
            'bond_radius': self.settings.bond_radius,
            'opengl_available': OPENGL_AVAILABLE
        }


# Utility functions for 3D rendering
def create_simple_renderer(width: int = 800, height: int = 600) -> Renderer3D:
    """
    Create a simple 3D renderer with default settings.
    
    Args:
        width: Viewport width
        height: Viewport height
        
    Returns:
        Configured 3D renderer
    """
    renderer = Renderer3D(width, height)
    return renderer


def render_molecule_to_console(molecule_3d: Molecule3D) -> None:
    """
    Render molecule information to console (fallback when OpenGL not available).
    
    Args:
        molecule_3d: Molecule to render
    """
    print("3D Molecule Rendering (Console Mode)")
    print("=" * 40)
    
    # Show atoms
    print(f"Atoms ({len(molecule_3d.molecule.atoms)}):")
    for i, atom in enumerate(molecule_3d.molecule.atoms):
        if atom.position_3d:
            print(f"  {i+1}. {atom.element.symbol} at ({atom.position_3d.x:.2f}, {atom.position_3d.y:.2f}, {atom.position_3d.z:.2f})")
        else:
            print(f"  {i+1}. {atom.element.symbol} at (no 3D coordinates)")
    
    # Show bonds
    print(f"\nBonds ({len(molecule_3d.molecule.bonds)}):")
    for i, bond in enumerate(molecule_3d.molecule.bonds):
        atom1_idx = molecule_3d.molecule.atoms.index(bond.atom1) + 1
        atom2_idx = molecule_3d.molecule.atoms.index(bond.atom2) + 1
        length_3d = bond.get_length_3d()
        length_str = f"{length_3d:.3f} Å" if length_3d else "no 3D coords"
        print(f"  {i+1}. {atom1_idx}-{atom2_idx} ({bond.order.name}, {length_str})")
    
    # Show molecular properties
    center = molecule_3d.get_center_of_mass()
    if center:
        print(f"\nCenter of mass: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})")
    
    surface_area = molecule_3d.calculate_surface_area()
    print(f"Surface area: {surface_area:.2f} Ų")
    
    bounding_box = molecule_3d.get_bounding_box()
    if bounding_box:
        min_pt, max_pt = bounding_box
        print(f"Bounding box: ({min_pt.x:.2f}, {min_pt.y:.2f}, {min_pt.z:.2f}) to ({max_pt.x:.2f}, {max_pt.y:.2f}, {max_pt.z:.2f})")
    
    print("=" * 40)