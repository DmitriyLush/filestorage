from typing import Optional

from app.models import Dir, Users_files
from app import db	

ROOT_dir = "/"

class Filesystem:
    def __init__(self, user_id):
      self.files = Files(user_id)
      self.dirs = Dirs(user_id)
      self._path = ROOT_dir

    def _basename(self) -> str:
        if self._path == ROOT_dir:
            return ROOT_dir
        return self._path.split('/')[-1]

    def retrieve_file(self, filepath: str) -> Optional[Users_files]:
        file = self.files.get_by_filename(filepath.split('/')[-1])
        return file
    
    def go(self, path):
        self._path = path

    def get_files(self):
        """
        1. Получаем папку по пути по которому стоим
        2. Получаем у папки ее id
        3. Получаем все файлы которые лежат в папке с id
        """
        dirname = self._basename()
        dir = self.dirs.get_by_dirname(dirname)
        if dir is None:
            return []
        dir_id = dir.id
        files = self.files.get_from_dir(dir_id)

        return files

    def get_dirs(self):
        dirname = self._basename()
        dir = self.dirs.get_by_dirname(dirname)
        if dir is None:
            return []
        dir_id = dir.id
        dirs = self.dirs.get_from_dir(dir_id)
        
        return dirs

    def get_all(self):
        files = self.get_files()
        dirs = self.get_dirs()

        return files, dirs

    def create_file(self, file):
        dirname = self._basename()
        parent_dir = self.dirs.get_by_dirname(dirname)
        self.files.create_file(file, parent_dir)

    def create_dir(self, new_dirname):
        dirname = self._basename()
        parent_dir = self.dirs.get_by_dirname(dirname)
        self.dirs.create_dir(new_dirname, parent_dir)


class Files:
    def __init__(self, user_id):
        self._user_id = user_id

    def get_by_filename(self, filename: str) -> Optional[Users_files]:
        file = Users_files.query.filter_by(name=filename, user_id=self._user_id).first()
        return file
    
    def get_from_dir(self, dir_id):
        files = Users_files.query.filter_by(parent=dir_id, user_id=self._user_id).all()
        return files

    def create_file(self, file, parent_dir):
        new_file = Users_files(
            name=file.filename,
            data=file.read(),
            user_id=self._user_id,
            mimetype=file.mimetype,
            parent=parent_dir.id
        )
        db.session.add(new_file)
        db.session.commit()


class Dirs:
    def __init__(self, user_id):
        self._user_id = user_id
        root_dir = self.get_by_dirname(ROOT_dir)
        print(root_dir)
        if root_dir is None:
            self.create_dir(ROOT_dir)
    
    def get_by_dirname(self, dirname: str) -> Optional[Dir]:
        dir = Dir.query.filter_by(name=dirname, user_id=self._user_id).first()
        return dir

    def get_from_dir(self, dir_id):
        dirs = Dir.query.filter_by(parent=dir_id, user_id=self._user_id).all()
        return dirs
    
    def create_dir(self, dirname, parent_dir=None):
        new_dir = Dir(
            name=dirname,
            user_id=self._user_id,
            parent=parent_dir.id if parent_dir is not None else None
        )
        db.session.add(new_dir)
        db.session.commit()
