# to use this script, need to install
# pip install langchain langchain-community pypdf


from langchain_community.document_loaders import PyPDFLoader

# loader = PyPDFLoader("./testing_files/inputs/pdf-without-images-1-page.pdf")
loader = PyPDFLoader("./testing_files/inputs/pdf-with-images.pdf")
documents = loader.load()  # Loads entire PDF
# documents = loader.lazy_load()  # Loads pages as needed


print(len(documents))

for doc in documents:
    print("----------- CONTENT STARTS --------------\n")
    print(doc.page_content)

    print("\n----------- CONTENT ENDS ----------------")
    print("----------- METADATA STARTS --------------\n")

    if doc.metadata:
        print("---")
        for key, value in doc.metadata.items():
            print(f"{key}: {value}")
            print("---")

    print("\n----------- METADATA ENDS ----------------\n")
