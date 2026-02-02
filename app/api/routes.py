import os
from flask import jsonify, request, current_app, url_for
from werkzeug.utils import secure_filename
from . import api
from ..services.vision_service import vision_service
from ..models import db, ImageUpload
from flask_login import current_user

@api.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True) # Ensure directory exists
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Process Image
        try:
            results = vision_service.process_image(filepath)
            
            # Save to DB (optional/mocked if no user)
            # Create a comma-separated string of tags
            tags_str = ",".join(results['tags'])
            
            # Save upload to database
            user_id = current_user.id if current_user.is_authenticated else None
            
            upload_record = ImageUpload(
                filename=filename,
                original_filepath=filepath,
                processed_filepath=results['processed_image_path'],
                results=str(results),
                tags=tags_str,
                user_id=user_id # Authenticated user or None
            )
            db.session.add(upload_record)
            db.session.commit()

            # Emit Real-time Event
            # Import socketio locally to avoid circular imports if necessary, or from ..
            from .. import socketio
            
            # Prepare data for broadcast
            broadcast_data = {
                'username': current_user.name if current_user.is_authenticated else 'Guest',
                'filename': filename,
                'image_url': url_for('static', filename='uploads/' + results['processed_image_path']),
                'upload_date': upload_record.upload_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            socketio.emit('new_upload', broadcast_data)

            # Find Related Images
            related_images = []
            if results['tags']:
                # Find images that share at least one tag
                # Simple implementation: look for overlaps in tag string
                # For better performance, use a many-to-many relationship
                query = ImageUpload.query.filter(ImageUpload.id != upload_record.id)
                
                # Filter locally for demo or use LIKE for each tag
                # Using basic string search for first detected object as primary relation
                potential_matches = query.order_by(ImageUpload.upload_date.desc()).limit(10).all()
                for match in potential_matches:
                    match_tags = match.tags.split(',') if match.tags else []
                    if any(tag in match_tags for tag in results['tags']):
                         related_images.append(url_for('static', filename='uploads/' + match.processed_filepath))
            
            results['related_images'] = related_images
            results['processed_image_url'] = url_for('static', filename='uploads/' + results['processed_image_path'])
            results['extracted_items_urls'] = [url_for('static', filename='uploads/crops/' + item) for item in results['extracted_items']]
            
            return jsonify(results), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
