add file:
echo "File for raspberry Olega2" > test-fileOleg2.txt
gsutil cp test-fileOleg2.txt gs://encoded-shape-452012-k8-secure-downloads/
gsutil cat gs://encoded-shape-452012-k8-secure-downloads/test-fileOleg2.txt

Чтобы предоставить права доступа к файлу в бакете Google Cloud Storage, вам нужно использовать команду gsutil acl. 
Вот как можно предоставить публичный доступ к файлу для чтения:
gsutil acl ch -u AllUsers:R gs://encoded-shape-452012-k8-secure-downloads/test-file4.txt