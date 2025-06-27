## Creating layer for jitsi_records_remover lambda

pip install --target ./python -r bucket_records_remover_requirements.txt
zip -r python.zip ./python/

`Lambda - Layers - Add layer - Layer source - Create a new layer`. 
Upload zip-file there. After that choose `Custom layer` in `Layer source`.

Remove `python` directory and zip-file.