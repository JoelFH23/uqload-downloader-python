import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional
import tempfile
from uuid import uuid4


class ParallelDownloader:
    """
    Téléchargeur ultra-rapide utilisant des segments parallèles.
    Divise le fichier en plusieurs parties et les télécharge simultanément.
    """
    
    def __init__(
        self,
        url: str,
        filename: str,
        output_dir: str,
        total_size: int,
        headers: dict,
        on_progress_callback: Callable = None,
        num_segments: int = 4
    ):
        self.url = url
        self.filename = filename
        self.output_dir = output_dir
        self.total_size = total_size
        self.headers = headers
        self.on_progress_callback = on_progress_callback
        self.num_segments = min(num_segments, 20)  # Max 20 segments pour vitesse ULTRA
        self.bytes_downloaded = 0
        self.segment_size = total_size // self.num_segments
        
    def _download_segment(self, segment_id: int, start: int, end: int) -> tuple:
        """Télécharge un segment spécifique du fichier."""
        try:
            # Copier les headers et ajouter Range
            segment_headers = self.headers.copy()
            segment_headers["Range"] = f"bytes={start}-{end}"
            
            request = urllib.request.Request(self.url, headers=segment_headers)
            
            # Fichier temporaire pour ce segment
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_filename = temp_file.name
            temp_file.close()
            
            with urllib.request.urlopen(request, timeout=120) as response:  # Timeout ultra-long
                if response.getcode() not in [200, 206]:
                    return segment_id, None, f"HTTP {response.getcode()}"
                
                with open(temp_filename, "wb") as f:
                    chunk_size = 5 * 1024 * 1024  # 5MB chunks pour vitesse ULTRA
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        self.bytes_downloaded += len(chunk)
                        
                        # Mise à jour du progrès en temps réel pour voir l'avancée
                        if self.on_progress_callback:
                            self.on_progress_callback(self.bytes_downloaded, self.total_size)
            
            return segment_id, temp_filename, None
            
        except Exception as e:
            # Nettoyer le fichier temporaire en cas d'erreur
            if 'temp_filename' in locals() and os.path.exists(temp_filename):
                try:
                    os.unlink(temp_filename)
                except:
                    pass
            return segment_id, None, str(e)
    
    def _check_range_support(self) -> bool:
        """Vérifie si le serveur supporte les requêtes Range."""
        try:
            test_headers = self.headers.copy()
            test_headers["Range"] = "bytes=0-1"
            request = urllib.request.Request(self.url, headers=test_headers, method="HEAD")
            
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.getcode() == 206
        except Exception as e:
            print(f"⚠️  Erreur lors de la vérification Range: {e}")
            return False
    
    def download(self) -> str:
        """Télécharge le fichier en utilisant des segments parallèles."""
        destination = os.path.join(self.output_dir, self.filename)
        
        # Éviter l'écrasement
        if os.path.isfile(destination):
            base, ext = os.path.splitext(self.filename)
            destination = os.path.join(self.output_dir, f"{base}_{uuid4().hex}{ext}")
        
        # Skip la vérification Range pour plus de vitesse
        range_supported = False  # On essaie directement les segments
        
        print(f"🚀 Téléchargement par segments ({self.num_segments} segments parallèles)")
        
        # Calculer les segments
        segments = []
        for i in range(self.num_segments):
            start = i * self.segment_size
            if i == self.num_segments - 1:
                end = self.total_size - 1  # Dernier segment prend le reste
            else:
                end = start + self.segment_size - 1
            segments.append((i, start, end))
        
        # Télécharger tous les segments en parallèle
        temp_files = {}
        errors = []
        
        with ThreadPoolExecutor(max_workers=self.num_segments) as executor:
            future_to_segment = {
                executor.submit(self._download_segment, seg_id, start, end): (seg_id, start, end)
                for seg_id, start, end in segments
            }
            
            for future in as_completed(future_to_segment):
                seg_id, temp_filename, error = future.result()
                if error:
                    errors.append(f"Segment {seg_id}: {error}")
                else:
                    temp_files[seg_id] = temp_filename
        
        if errors:
            # Nettoyer les fichiers temporaires
            for temp_file in temp_files.values():
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            
            # Si trop d'erreurs, fallback vers téléchargement normal
            if len(errors) > self.num_segments // 2:  # Plus de la moitié des segments ont échoué
                print(f"⚠️  Trop d'erreurs avec les segments, fallback vers téléchargement normal")
                return self._download_normal(destination)
            else:
                raise Exception(f"Erreurs de téléchargement: {'; '.join(errors)}")
        
        # Assembler les segments
        print(f"🔧 Assemblage des segments...")
        with open(destination, "wb") as output_file:
            for i in range(self.num_segments):
                temp_file = temp_files[i]
                with open(temp_file, "rb") as segment_file:
                    output_file.write(segment_file.read())
                os.unlink(temp_file)  # Supprimer le fichier temporaire
        
        return destination
    
    def _download_normal(self, destination: str) -> str:
        """Téléchargement normal (fallback)."""
        print(f"📥 Téléchargement normal (fichier trop petit ou serveur incompatible)")
        
        request = urllib.request.Request(self.url, headers=self.headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(destination, "wb", buffering=10*1024*1024) as f:
                chunk_size = 10 * 1024 * 1024  # 10MB
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    self.bytes_downloaded += len(chunk)
                    if self.on_progress_callback:
                        self.on_progress_callback(self.bytes_downloaded, self.total_size)
        
        return destination
