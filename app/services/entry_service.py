from datetime import datetime
from flask import current_app
from app import db
from app.models.entry import Entry, EntryStatus
from app.models.tag import Tag

class EntryService:
    """
    Servicio para gestionar operaciones relacionadas con entradas (notas/ideas).
    """
    
    def create_entry(self, title, content, user_id, collection_id=None, tags=None):
        """
        Crea una nueva entrada en la base de datos.
        
        Args:
            title (str): Título de la entrada.
            content (str): Contenido de la entrada en formato Markdown.
            user_id (int): ID del usuario propietario.
            collection_id (int, opcional): ID de la colección a la que pertenece.
            tags (list, opcional): Lista de nombres de etiquetas.
            
        Returns:
            Entry: Instancia de la entrada creada.
        """
        entry = Entry(
            title=title,
            content=content,
            user_id=user_id,
            collection_id=collection_id,
            status=EntryStatus.BORRADOR.value
        )
        
        db.session.add(entry)
        db.session.flush()  # Para obtener el ID de la entrada
        
        # Procesamiento de etiquetas
        if tags:
            self._process_tags(entry, tags)
        
        db.session.commit()
        return entry
    
    def update_entry(self, entry_id, title=None, content=None, collection_id=None, tags=None):
        """
        Actualiza una entrada existente.
        
        Args:
            entry_id (int): ID de la entrada a actualizar.
            title (str, opcional): Nuevo título.
            content (str, opcional): Nuevo contenido.
            collection_id (int, opcional): Nueva colección.
            tags (list, opcional): Nueva lista de etiquetas.
            
        Returns:
            Entry: Entrada actualizada o None si no se encuentra.
        """
        entry = self.get_entry_by_id(entry_id)
        
        if not entry:
            return None
        
        if title is not None:
            entry.title = title
        
        if content is not None:
            entry.content = content
        
        if collection_id is not None:
            entry.collection_id = collection_id
        
        # Actualizar etiquetas si se proporcionan
        if tags is not None:
            # Eliminar todas las etiquetas actuales
            entry.tags = []
            # Añadir las nuevas etiquetas
            self._process_tags(entry, tags)
        
        entry.updated_at = datetime.utcnow()
        db.session.commit()
        
        return entry
    
    def get_entry_by_id(self, entry_id, include_deleted=False):
        """
        Obtiene una entrada por su ID.
        
        Args:
            entry_id (int): ID de la entrada.
            include_deleted (bool): Si se deben incluir entradas eliminadas.
            
        Returns:
            Entry: Entrada encontrada o None.
        """
        query = Entry.query.filter_by(id=entry_id)
        
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
            
        return query.first()
    
    def get_entries_by_user(self, user_id, include_deleted=False, page=1, per_page=20):
        """
        Obtiene todas las entradas de un usuario con paginación.
        
        Args:
            user_id (int): ID del usuario.
            include_deleted (bool): Si se deben incluir entradas eliminadas.
            page (int): Número de página para paginación.
            per_page (int): Entradas por página.
            
        Returns:
            Pagination: Objeto de paginación de SQLAlchemy con las entradas.
        """
        query = Entry.query.filter_by(user_id=user_id)
        
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
            
        return query.order_by(Entry.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def get_entries_by_collection(self, collection_id, include_deleted=False, page=1, per_page=20):
        """
        Obtiene todas las entradas de una colección con paginación.
        
        Args:
            collection_id (int): ID de la colección.
            include_deleted (bool): Si se deben incluir entradas eliminadas.
            page (int): Número de página para paginación.
            per_page (int): Entradas por página.
            
        Returns:
            Pagination: Objeto de paginación de SQLAlchemy con las entradas.
        """
        query = Entry.query.filter_by(collection_id=collection_id)
        
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
            
        return query.order_by(Entry.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def get_entries_in_trash(self, user_id, page=1, per_page=20):
        """
        Obtiene todas las entradas eliminadas (en papelera) de un usuario.
        
        Args:
            user_id (int): ID del usuario.
            page (int): Número de página para paginación.
            per_page (int): Entradas por página.
            
        Returns:
            Pagination: Objeto de paginación de SQLAlchemy con las entradas.
        """
        return Entry.query.filter_by(
            user_id=user_id, 
            is_deleted=True
        ).order_by(Entry.deleted_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def delete_entry(self, entry_id):
        """
        Realiza un borrado lógico de una entrada.
        
        Args:
            entry_id (int): ID de la entrada a eliminar.
            
        Returns:
            Entry: Entrada eliminada o None si no se encuentra.
        """
        entry = self.get_entry_by_id(entry_id)
        
        if not entry:
            return None
        
        entry.soft_delete()
        db.session.commit()
        
        return entry
    
    def restore_entry(self, entry_id):
        """
        Restaura una entrada previamente eliminada.
        
        Args:
            entry_id (int): ID de la entrada a restaurar.
            
        Returns:
            Entry: Entrada restaurada o None si no se encuentra.
        """
        # Usamos include_deleted para poder encontrar entradas eliminadas
        entry = self.get_entry_by_id(entry_id, include_deleted=True)
        
        if not entry or not entry.is_deleted:
            return None
        
        entry.is_deleted = False
        entry.deleted_at = None
        db.session.commit()
        
        return entry
    
    def search_entries(self, user_id, query_text, page=1, per_page=20):
        """
        Busca entradas que coincidan con un texto de búsqueda.
        
        Args:
            user_id (int): ID del usuario propietario.
            query_text (str): Texto a buscar.
            page (int): Número de página para paginación.
            per_page (int): Entradas por página.
            
        Returns:
            Pagination: Objeto de paginación de SQLAlchemy con las entradas encontradas.
        """
        search_query = f"%{query_text}%"
        
        return Entry.query.filter(
            Entry.user_id == user_id,
            Entry.is_deleted == False,
            (Entry.title.ilike(search_query) | Entry.content.ilike(search_query))
        ).order_by(Entry.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def _process_tags(self, entry, tag_names):
        """
        Método privado para procesar etiquetas de una entrada.
        
        Args:
            entry (Entry): Entrada a la que se añadirán las etiquetas.
            tag_names (list): Lista de nombres de etiquetas.
        """
        for tag_name in tag_names:
            # Normalizar nombre de etiqueta
            tag_name = tag_name.strip().lower()
            if not tag_name:
                continue
                
            # Buscar si la etiqueta ya existe
            tag = Tag.query.filter_by(name=tag_name).first()
            
            # Crear nueva etiqueta si no existe
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
            
            # Añadir etiqueta a la entrada
            entry.add_tag(tag) 