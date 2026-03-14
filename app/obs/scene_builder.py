import logging

from app.config import load_scene_templates
from app.obs.connection import obs_connection
from app.obs.source_manager import source_manager

logger = logging.getLogger(__name__)


class SceneBuilder:
    def __init__(self):
        self._templates = load_scene_templates()

    def get_templates(self) -> dict:
        return self._templates.get("templates", {})

    def build_scene(self, template_name: str, scene_name: str = None) -> bool:
        """Create or update a scene from a template."""
        templates = self._templates.get("templates", {})
        if template_name not in templates:
            logger.error("Template '%s' not found", template_name)
            return False

        template = templates[template_name]
        if scene_name is None:
            scene_name = template.get("label", template_name)

        client = obs_connection.client
        if not client:
            logger.error("OBS not connected")
            return False

        # Create the scene (ignore error if it already exists)
        try:
            client.create_scene(scene_name)
            logger.info("Created scene '%s'", scene_name)
        except Exception:
            logger.info("Scene '%s' already exists, updating", scene_name)

        # Remove existing items from the scene
        try:
            items = source_manager.get_scene_items(scene_name)
            for item in items:
                try:
                    client.remove_scene_item(scene_name, item["sceneItemId"])
                except Exception:
                    pass
        except Exception:
            pass

        # Add sources according to template layout
        canvas = self._templates.get("canvas", {"width": 1920, "height": 1080})
        for slot in template["layout"]:
            source_name = slot["source"]
            item_id = source_manager.add_existing_source(scene_name, source_name)
            if item_id is not None:
                source_manager.set_item_transform(
                    scene_name, item_id,
                    x=slot["x"], y=slot["y"],
                    width=slot["width"], height=slot["height"]
                )

        logger.info("Built scene '%s' from template '%s'", scene_name, template_name)
        return True

    def build_lower_third_scene(self, name: str, title: str) -> bool:
        """Create a browser source overlay for lower thirds."""
        client = obs_connection.client
        if not client:
            return False

        lt_config = self._templates.get("lower_third", {})
        html = f"""
        <html>
        <head><style>
            body {{ margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; }}
            .lower-third {{
                position: absolute;
                bottom: 0; left: 0;
                width: {lt_config.get('width', 600)}px;
                padding: 12px 24px;
                background: {lt_config.get('bg_color', 'rgba(0,0,0,0.75)')};
                border-left: 4px solid {lt_config.get('accent_color', '#ff6b35')};
                animation: slideIn 0.5s ease-out;
            }}
            .name {{ color: {lt_config.get('text_color', '#fff')}; font-size: 28px; font-weight: bold; }}
            .title {{ color: {lt_config.get('accent_color', '#ff6b35')}; font-size: 18px; margin-top: 2px; }}
            @keyframes slideIn {{ from {{ transform: translateX(-100%); }} to {{ transform: translateX(0); }} }}
        </style></head>
        <body><div class="lower-third"><div class="name">{name}</div><div class="title">{title}</div></div></body>
        </html>
        """
        # The browser source URL will be a data URI or local file
        # For simplicity, we write the HTML to a temp file
        import tempfile, os
        lt_dir = os.path.join(tempfile.gettempdir(), "uncapped_lt")
        os.makedirs(lt_dir, exist_ok=True)
        lt_path = os.path.join(lt_dir, "lower_third.html")
        with open(lt_path, "w") as f:
            f.write(html)

        local_url = f"file:///{lt_path.replace(os.sep, '/')}"
        input_name = "Lower Third"

        # Remove existing lower third if present
        try:
            source_manager.remove_input(input_name)
        except Exception:
            pass

        # Get current scene and add browser source
        try:
            current = client.get_current_program_scene().scene_name
            item_id = source_manager.create_input(
                current, input_name, "browser_source",
                {
                    "url": local_url,
                    "width": lt_config.get("width", 600),
                    "height": lt_config.get("height", 100),
                    "css": "",
                },
                enabled=True
            )
            if item_id is not None:
                source_manager.set_item_transform(
                    current, item_id,
                    x=lt_config.get("x", 100),
                    y=lt_config.get("y", 900),
                    width=lt_config.get("width", 600),
                    height=lt_config.get("height", 100),
                )
            return True
        except Exception as e:
            logger.error("Failed to create lower third: %s", e)
            return False

    def hide_lower_third(self) -> bool:
        try:
            return source_manager.remove_input("Lower Third")
        except Exception:
            return False


scene_builder = SceneBuilder()
