# 🚀 Ragswift - Empowering Scalable RAG Framework for Effortless Document Ingestion and Retrieval at Scale

## 🔗 Overview

Ragswift is an advanced RAG framework meticulously crafted for the efficient handling of extensive document ingestion and retrieval tasks. Eliminate concerns associated with document management within your RAG pipeline, as this scalable solution allows for seamless self-hosting, enabling centralized control and sharing of embeddings.

It harnesses the power of distributed computing through Ray, empowering users to effortlessly process vast document sets in parallel across multiple CPU and GPU nodes. The incorporation of Qdrant disk-based indexing and storage guarantees robust support for the scale of billions of vectors, positioning Ragswift as a formidable choice for large-scale applications.

Moreover, Ragswift will soon feature compute autoscaling capabilities using kubernetes, ensuring that you only pay for the compute resources you use. This cost-efficient model enhances the platform's flexibility, allowing users to scale their infrastructure dynamically in response to varying workloads, optimizing both performance and cost-effectiveness.

## 🔗 Getting Started (Docker)

Follow these steps to get started with the RAG Framework:

1. Clone the repository
2. Configure your settings: Edit the configuration file (.env) to customize the framework based on your requirements. The sample .env is given in .env.example
3. Run using docker: `docker compose up`
4. The api docs will be availaible at `http://localhost:5005/docs`

## 🔗 Demo

https://github.com/shivamsanju/ragswift/assets/103770073/ed55385f-8dba-446d-a5a6-9f447b1c0209

## 🔗 Key Features

### 1. Distributed Computing with Ray 🌐

The RAG Framework employs Ray for distributed computing, enabling parallel document ingestion across multiple CPU and GPU nodes. This ensures optimal utilization of resources for efficient and scalable processing.

### 2. Qdrant Disk-Based Indexing 💽

To support the scale of billions of vectors, the framework integrates Qdrant disk-based indexing. This technology provides high-performance indexing capabilities, facilitating rapid and precise retrieval of relevant information.

### 3. REST APIs for Seamless Integration 🔄

RAG Framework offers REST APIs for convenient asset ingestion from popular sources such as S3 and GitHub. The APIs are also designed for efficient retrieval, ensuring a smooth and seamless integration into your existing workflows.

### 4. Ray Serve for API Scalability ⚙️

REST APIs are served using Ray Serve, allowing for easy scalability across multiple GPU and CPU nodes. This ensures that the framework adapts to the demands of your application, providing consistent performance even in dynamic environments.

### 5. Configurability at Your Fingertips 🛠️
The RAG Framework is highly configurable, allowing users to tailor the system to their specific needs. Key configuration options include the number of CPUs/GPUs to use, the choice of embedding model, chunk size, reranker model, and more.


## 🔗 Upcoming Features

- [ ] **Autoscaled Deployment on Kubernetes**
  - Implement autoscaling mechanisms on Kubernetes for optimized deployment costs and efficient resource usage.

- [ ] **Admin UI for Document Management**
  - Develop a centralized admin UI for seamless management of documents, ingestion jobs, and infrastructure.

- [ ] **Configurable Projects with Embedding Dimension Models**
  - Enable configurable projects with the flexibility to experiment with different embedding dimension, chunk size, embedding models etc within a single deployment.

- [ ] **Observability Tool**
  - Integrate an observability tool to compare the performance of embeddings across various parameters, to improve the quality of embeddings backed by experiments.

- [ ] **Access Management**
  - Introduce access management features to enhance security and control over document access, catering to different user roles.

