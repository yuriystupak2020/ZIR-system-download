add file:
echo "Content of forth file 4444" > test-file4.txt
gsutil cp test-file4.txt gs://encoded-shape-452012-k8-secure-downloads/

Чтобы предоставить права доступа к файлу в бакете Google Cloud Storage, вам нужно использовать команду gsutil acl. 
Вот как можно предоставить публичный доступ к файлу для чтения:
gsutil acl ch -u AllUsers:R gs://encoded-shape-452012-k8-secure-downloads/test-file4.txt