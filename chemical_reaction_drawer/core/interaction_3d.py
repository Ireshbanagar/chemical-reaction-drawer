"""
3D interaction controls for molecular visualization.

This module provides mouse-based rotation controls, zoom functionality,
and navigation tools for 3D molecular visualization.
"""

import math
from typing import Optional, Tuple, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from .models import Point3D
from .renderer_3d import Renderer3D, Camera3D
from .molecule_3d import Molecule3D


class InteractionMode(Enum):
    """Enumeration of different interaction modes."""
    ROTATE = "rotate"
    ZOOM = "zoom"
    PAN = "pan"
    SELECT = "select"


class MouseButton(Enum):
    """Mouse button enumeration."""
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3


@dataclass
class MouseState:
    """
    Tracks the current state of mouse input.
    
    Attributes:
        position: Current mouse position (x, y)
        last_position: Previous mouse position
        buttons_pressed: Set of currently pressed mouse buttons
        is_dragging: Whether the mouse is currently being dragged
        drag_start_position: Position where dragging started
    """
    position: Tuple[int, int] = (0, 0)
    last_position: Tuple[int, int] = (0, 0)
    buttons_pressed: set = field(default_factory=set)
    is_dragging: bool = False
    drag_start_position: Tuple[int, int] = (0, 0)
    
    def update_position(self, x: int, y: int) -> None:
        """Update mouse position."""
        self.last_position = self.position
        self.position = (x, y)
    
    def get_delta(self) -> Tuple[int, int]:
        """Get the change in mouse position since last update."""
        return (
            self.position[0] - self.last_position[0],
            self.position[1] - self.last_position[1]
        )
    
    def start_drag(self, button: MouseButton) -> None:
        """Start dragging with the specified button."""
        self.buttons_pressed.add(button)
        self.is_dragging = True
        self.drag_start_position = self.position
    
    def end_drag(self, button: MouseButton) -> None:
        """End dragging for the specified button."""
        self.buttons_pressed.discard(button)
        if not self.buttons_pressed:
            self.is_dragging = False


@dataclass
class InteractionSettings:
    """
    Settings for 3D interaction controls.
    
    Attributes:
        rotation_sensitivity: Sensitivity for rotation controls
        zoom_sensitivity: Sensitivity for zoom controls
        pan_sensitivity: Sensitivity for panning controls
        invert_y_rotation: Whether to invert Y-axis rotation
        smooth_interactions: Whether to apply smoothing to interactions
        double_click_threshold: Time threshold for double-click detection (ms)
        drag_threshold: Minimum pixel distance to start dragging
    """
    rotation_sensitivity: float = 1.0
    zoom_sensitivity: float = 1.0
    pan_sensitivity: float = 1.0
    invert_y_rotation: bool = False
    smooth_interactions: bool = True
    double_click_threshold: int = 300
    drag_threshold: int = 3


class InteractionController:
    """
    Handles 3D interaction controls for molecular visualization.
    
    This class manages mouse-based rotation, zoom, pan operations,
    and provides navigation tools for 3D molecular structures.
    """
    
    def __init__(self, renderer: Renderer3D):
        """
        Initialize the interaction controller.
        
        Args:
            renderer: 3D renderer to control
        """
        self.renderer = renderer
        self.settings = InteractionSettings()
        self.mouse_state = MouseState()
        self.current_mode = InteractionMode.ROTATE
        
        # Callback functions for interaction events
        self.callbacks: Dict[str, Callable] = {}
        
        # Navigation state
        self.auto_rotate = False
        self.auto_rotate_speed = 1.0
        self.last_interaction_time = 0
        
        # View presets
        self.view_presets = {
            'front': (0.0, 0.0),
            'back': (180.0, 0.0),
            'left': (-90.0, 0.0),
            'right': (90.0, 0.0),
            'top': (0.0, 90.0),
            'bottom': (0.0, -90.0),
            'isometric': (45.0, 35.26)
        }
    
    def set_interaction_mode(self, mode: InteractionMode) -> None:
        """
        Set the current interaction mode.
        
        Args:
            mode: New interaction mode
        """
        self.current_mode = mode
        self._trigger_callback('mode_changed', mode)
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback function for interaction events.
        
        Args:
            event: Event name (e.g., 'rotation_changed', 'zoom_changed')
            callback: Callback function to register
        """
        self.callbacks[event] = callback
    
    def _trigger_callback(self, event: str, *args, **kwargs) -> None:
        """Trigger a registered callback if it exists."""
        if event in self.callbacks:
            self.callbacks[event](*args, **kwargs)
    
    def handle_mouse_press(self, x: int, y: int, button: MouseButton) -> None:
        """
        Handle mouse button press events.
        
        Args:
            x: Mouse X coordinate
            y: Mouse Y coordinate
            button: Mouse button that was pressed
        """
        self.mouse_state.update_position(x, y)
        self.mouse_state.start_drag(button)
        
        # Stop auto-rotation when user interacts
        self.auto_rotate = False
        
        self._trigger_callback('mouse_press', x, y, button)
    
    def handle_mouse_release(self, x: int, y: int, button: MouseButton) -> None:
        """
        Handle mouse button release events.
        
        Args:
            x: Mouse X coordinate
            y: Mouse Y coordinate
            button: Mouse button that was released
        """
        self.mouse_state.update_position(x, y)
        
        # Check if this was a click (not a drag)
        drag_distance = math.sqrt(
            (x - self.mouse_state.drag_start_position[0]) ** 2 +
            (y - self.mouse_state.drag_start_position[1]) ** 2
        )
        
        if drag_distance < self.settings.drag_threshold:
            self._handle_click(x, y, button)
        
        self.mouse_state.end_drag(button)
        self._trigger_callback('mouse_release', x, y, button)
    
    def handle_mouse_move(self, x: int, y: int) -> None:
        """
        Handle mouse movement events.
        
        Args:
            x: Mouse X coordinate
            y: Mouse Y coordinate
        """
        self.mouse_state.update_position(x, y)
        
        if self.mouse_state.is_dragging:
            self._handle_drag()
        
        self._trigger_callback('mouse_move', x, y)
    
    def handle_mouse_wheel(self, delta: float) -> None:
        """
        Handle mouse wheel events for zooming.
        
        Args:
            delta: Wheel delta (positive = zoom in, negative = zoom out)
        """
        zoom_factor = 1.0 + (delta * self.settings.zoom_sensitivity * 0.1)
        
        # Clamp zoom factor to reasonable range
        zoom_factor = max(0.1, min(10.0, zoom_factor))
        
        self.renderer.handle_zoom(zoom_factor)
        self._trigger_callback('zoom_changed', zoom_factor)
    
    def _handle_click(self, x: int, y: int, button: MouseButton) -> None:
        """Handle mouse click events (not drag)."""
        if self.current_mode == InteractionMode.SELECT:
            # TODO: Implement atom/bond selection
            self._trigger_callback('selection_click', x, y, button)
    
    def _handle_drag(self) -> None:
        """Handle mouse drag operations based on current mode and buttons."""
        delta_x, delta_y = self.mouse_state.get_delta()
        
        if not delta_x and not delta_y:
            return
        
        # Apply Y-axis inversion if enabled
        if self.settings.invert_y_rotation:
            delta_y = -delta_y
        
        if MouseButton.LEFT in self.mouse_state.buttons_pressed:
            if self.current_mode == InteractionMode.ROTATE:
                self._handle_rotation(delta_x, delta_y)
            elif self.current_mode == InteractionMode.PAN:
                self._handle_pan(delta_x, delta_y)
        
        elif MouseButton.MIDDLE in self.mouse_state.buttons_pressed:
            # Middle mouse button for panning
            self._handle_pan(delta_x, delta_y)
        
        elif MouseButton.RIGHT in self.mouse_state.buttons_pressed:
            # Right mouse button for zooming
            zoom_delta = -delta_y * 0.01  # Convert to zoom factor
            zoom_factor = 1.0 + zoom_delta
            self.renderer.handle_zoom(zoom_factor)
            self._trigger_callback('zoom_changed', zoom_factor)
    
    def _handle_rotation(self, delta_x: int, delta_y: int) -> None:
        """Handle rotation interaction."""
        # Convert pixel movement to rotation angles
        rotation_x = delta_x * self.settings.rotation_sensitivity * 0.5
        rotation_y = delta_y * self.settings.rotation_sensitivity * 0.5
        
        self.renderer.handle_rotation(rotation_x, rotation_y)
        self._trigger_callback('rotation_changed', rotation_x, rotation_y)
    
    def _handle_pan(self, delta_x: int, delta_y: int) -> None:
        """Handle panning interaction."""
        # Convert pixel movement to world space movement
        pan_x = delta_x * self.settings.pan_sensitivity * 0.01
        pan_y = -delta_y * self.settings.pan_sensitivity * 0.01  # Invert Y for natural panning
        
        # Apply panning to camera target
        camera = self.renderer.camera
        
        # Calculate right and up vectors for camera-relative panning
        # This is a simplified implementation - could be improved with proper vector math
        camera.target = Point3D(
            camera.target.x + pan_x,
            camera.target.y + pan_y,
            camera.target.z
        )
        
        # Update camera position to maintain relative position
        direction = Point3D(
            camera.position.x - camera.target.x,
            camera.position.y - camera.target.y,
            camera.position.z - camera.target.z
        )
        
        camera.position = Point3D(
            camera.target.x + direction.x,
            camera.target.y + direction.y,
            camera.target.z + direction.z
        )
        
        self._trigger_callback('pan_changed', pan_x, pan_y)
    
    def reset_view(self, molecule_3d: Optional[Molecule3D] = None) -> None:
        """
        Reset the camera view to default position.
        
        Args:
            molecule_3d: Optional molecule to focus on
        """
        if molecule_3d:
            self.renderer.reset_view(molecule_3d)
        else:
            # Reset to default view
            self.renderer.camera.position = Point3D(0.0, 0.0, 10.0)
            self.renderer.camera.target = Point3D(0.0, 0.0, 0.0)
            self.renderer.camera.up = Point3D(0.0, 1.0, 0.0)
        
        self._trigger_callback('view_reset')
    
    def set_view_preset(self, preset_name: str, molecule_3d: Optional[Molecule3D] = None) -> None:
        """
        Set camera to a predefined view.
        
        Args:
            preset_name: Name of the view preset
            molecule_3d: Optional molecule to focus on
        """
        if preset_name not in self.view_presets:
            raise ValueError(f"Unknown view preset: {preset_name}")
        
        # Reset view first
        self.reset_view(molecule_3d)
        
        # Apply preset rotation
        rotation_x, rotation_y = self.view_presets[preset_name]
        self.renderer.camera.rotate_around_target(rotation_x, rotation_y)
        
        self._trigger_callback('view_preset_changed', preset_name)
    
    def start_auto_rotation(self, speed: float = 1.0) -> None:
        """
        Start automatic rotation animation.
        
        Args:
            speed: Rotation speed (degrees per update)
        """
        self.auto_rotate = True
        self.auto_rotate_speed = speed
        self._trigger_callback('auto_rotation_started', speed)
    
    def stop_auto_rotation(self) -> None:
        """Stop automatic rotation animation."""
        self.auto_rotate = False
        self._trigger_callback('auto_rotation_stopped')
    
    def update_auto_rotation(self) -> None:
        """Update automatic rotation (call this in your render loop)."""
        if self.auto_rotate:
            self.renderer.handle_rotation(self.auto_rotate_speed, 0.0)
    
    def fit_to_view(self, molecule_3d: Molecule3D, padding: float = 1.2) -> None:
        """
        Adjust camera to fit the molecule in view.
        
        Args:
            molecule_3d: Molecule to fit in view
            padding: Padding factor around the molecule
        """
        bounding_box = molecule_3d.get_bounding_box()
        if not bounding_box:
            self.reset_view(molecule_3d)
            return
        
        min_pt, max_pt = bounding_box
        
        # Calculate molecule size
        size = max(
            abs(max_pt.x - min_pt.x),
            abs(max_pt.y - min_pt.y),
            abs(max_pt.z - min_pt.z)
        )
        
        # Calculate center
        center = Point3D(
            (min_pt.x + max_pt.x) / 2,
            (min_pt.y + max_pt.y) / 2,
            (min_pt.z + max_pt.z) / 2
        )
        
        # Set camera target to center
        self.renderer.camera.target = center
        
        # Calculate appropriate distance based on field of view
        fov_rad = math.radians(self.renderer.camera.fov)
        distance = (size * padding) / (2 * math.tan(fov_rad / 2))
        
        # Maintain current viewing direction but adjust distance
        current_direction = Point3D(
            self.renderer.camera.position.x - self.renderer.camera.target.x,
            self.renderer.camera.position.y - self.renderer.camera.target.y,
            self.renderer.camera.position.z - self.renderer.camera.target.z
        )
        
        current_distance = self.renderer.camera.get_distance_to_target()
        if current_distance > 0:
            scale = distance / current_distance
            self.renderer.camera.position = Point3D(
                center.x + current_direction.x * scale,
                center.y + current_direction.y * scale,
                center.z + current_direction.z * scale
            )
        
        self._trigger_callback('fit_to_view', molecule_3d)
    
    def get_interaction_info(self) -> Dict[str, Any]:
        """
        Get information about the current interaction state.
        
        Returns:
            Dictionary containing interaction information
        """
        return {
            'current_mode': self.current_mode.value,
            'mouse_position': self.mouse_state.position,
            'is_dragging': self.mouse_state.is_dragging,
            'buttons_pressed': [btn.value for btn in self.mouse_state.buttons_pressed],
            'auto_rotate': self.auto_rotate,
            'auto_rotate_speed': self.auto_rotate_speed,
            'settings': {
                'rotation_sensitivity': self.settings.rotation_sensitivity,
                'zoom_sensitivity': self.settings.zoom_sensitivity,
                'pan_sensitivity': self.settings.pan_sensitivity,
                'invert_y_rotation': self.settings.invert_y_rotation,
                'smooth_interactions': self.settings.smooth_interactions
            },
            'available_presets': list(self.view_presets.keys())
        }


class NavigationTools:
    """
    Additional navigation tools and utilities for 3D interaction.
    """
    
    @staticmethod
    def create_orbit_animation(controller: InteractionController, 
                             duration: float = 10.0, 
                             axis: str = 'y') -> Callable:
        """
        Create an orbit animation function.
        
        Args:
            controller: Interaction controller
            duration: Animation duration in seconds
            axis: Axis to orbit around ('x', 'y', or 'z')
            
        Returns:
            Animation update function
        """
        start_time = None
        
        def update_orbit(current_time: float) -> bool:
            nonlocal start_time
            if start_time is None:
                start_time = current_time
            
            elapsed = current_time - start_time
            if elapsed >= duration:
                return False  # Animation complete
            
            # Calculate rotation amount
            progress = elapsed / duration
            rotation_amount = 360.0 * progress
            
            if axis == 'y':
                controller.renderer.handle_rotation(1.0, 0.0)
            elif axis == 'x':
                controller.renderer.handle_rotation(0.0, 1.0)
            else:  # z-axis
                # Z-axis rotation is more complex, skip for now
                pass
            
            return True  # Continue animation
        
        return update_orbit
    
    @staticmethod
    def create_zoom_animation(controller: InteractionController,
                            target_distance: float,
                            duration: float = 2.0) -> Callable:
        """
        Create a smooth zoom animation.
        
        Args:
            controller: Interaction controller
            target_distance: Target camera distance
            duration: Animation duration in seconds
            
        Returns:
            Animation update function
        """
        start_time = None
        start_distance = None
        
        def update_zoom(current_time: float) -> bool:
            nonlocal start_time, start_distance
            if start_time is None:
                start_time = current_time
                start_distance = controller.renderer.camera.get_distance_to_target()
            
            elapsed = current_time - start_time
            if elapsed >= duration:
                return False  # Animation complete
            
            # Calculate smooth interpolation
            progress = elapsed / duration
            # Use ease-in-out curve
            smooth_progress = 3 * progress**2 - 2 * progress**3
            
            current_distance = start_distance + (target_distance - start_distance) * smooth_progress
            zoom_factor = current_distance / controller.renderer.camera.get_distance_to_target()
            
            controller.renderer.handle_zoom(zoom_factor)
            
            return True  # Continue animation
        
        return update_zoom


# Utility functions for interaction setup
def create_interaction_controller(renderer: Renderer3D) -> InteractionController:
    """
    Create an interaction controller with default settings.
    
    Args:
        renderer: 3D renderer to control
        
    Returns:
        Configured interaction controller
    """
    return InteractionController(renderer)


def setup_standard_interactions(controller: InteractionController) -> None:
    """
    Set up standard interaction callbacks and behaviors.
    
    Args:
        controller: Interaction controller to configure
    """
    # Register standard callbacks
    def on_rotation_changed(delta_x, delta_y):
        print(f"Rotation: {delta_x:.1f}, {delta_y:.1f}")
    
    def on_zoom_changed(zoom_factor):
        print(f"Zoom: {zoom_factor:.2f}")
    
    def on_view_reset():
        print("View reset")
    
    controller.register_callback('rotation_changed', on_rotation_changed)
    controller.register_callback('zoom_changed', on_zoom_changed)
    controller.register_callback('view_reset', on_view_reset)