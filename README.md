# 🚀 RAG Framework for Scalable Document Ingestion and Retrieval

## Overview

Welcome to the RAG Framework, a cutting-edge solution designed for scalable document ingestion and retrieval. Leveraging distributed computing with Ray, this framework empowers users to seamlessly process vast amounts of documents in parallel across multiple CPU and GPU nodes. The inclusion of Qdrant disk-based indexing ensures support for the scale of billions of vectors, making it a robust choice for large-scale applications.

## Demo

https://github.com/shivamsanju/ragswift/assets/103770073/ed55385f-8dba-446d-a5a6-9f447b1c0209

## Key Features

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

## Getting Started using docker

Follow these steps to get started with the RAG Framework:

1. Clone the repository
2. Configure your settings: Edit the configuration file (.env) to customize the framework based on your requirements. The sample .env is given in .env.example
3. Run using docker: `docker compose up`

