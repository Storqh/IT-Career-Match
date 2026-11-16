#!/usr/bin/env python3
"""
Create sample CVs for different job categories matching existing jobs on the web.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database.database import create_cv, get_skill_id_by_name, add_student_skill
from ai.skill_extractor import extract_skills
from werkzeug.security import generate_password_hash

# Sample CVs for different job categories
SAMPLE_CVS = [
    {
        "email": "test_otp2@example.com",
        "filename": "cv_ai_engineer.txt",
        "title": "AI Engineer / ML Engineer",
        "category": "AI / Machine Learning",
        "content": """
NGUYỄN VĂN A
AI Engineer | Machine Learning Engineer
Email: nguyenvana@email.com | Phone: 0901234567 | LinkedIn: linkedin.com/in/nguyenvana
GitHub: github.com/nguyenvana

TÓM TẮT
AI Engineer với 3 năm kinh nghiệm xây dựng, huấn luyện và triển khai mô hình Machine Learning/Deep Learning.
Thành thạo Python, TensorFlow, PyTorch, scikit-learn. Có kinh nghiệm triển khai model lên production với Docker, Kubernetes.
Đã phát triển các giải pháp Computer Vision, NLP và Recommendation System cho các dự án thực tế.

KỸ NĂNG CHUYÊN MÔN
- Machine Learning: Supervised/Unsupervised Learning, Ensemble Methods, Model Evaluation, Hyperparameter Tuning
- Deep Learning: CNN, RNN, LSTM, Transformer, BERT, GPT, Transfer Learning
- Frameworks: TensorFlow 2.x, PyTorch, Keras, Hugging Face Transformers, OpenCV
- MLOps: Docker, Kubernetes, MLflow, Kubeflow, Model Serving (TensorFlow Serving, TorchServe)
- Data: Pandas, NumPy, SQL, PostgreSQL, MongoDB, Apache Spark, Data Preprocessing, Feature Engineering
- Cloud: AWS (SageMaker, EC2, S3, Lambda), GCP (Vertex AI), Azure ML
- Programming: Python, C++, JavaScript, SQL, Bash

KINH NGHIỆM LÀM VIỆC

Senior AI Engineer | CyberShield Technology | 2022 - Hiện tại
- Xây dựng và huấn luyện mô hình Machine Learning cho hệ thống phát hiện gian lận (fraud detection) với độ chính xác 97%
- Tiền xử lý và phân tích dữ liệu 10TB+ hàng ngày, xây dựng feature store cho team Data Science
- Triển khai mô hình lên production với Docker + Kubernetes, giảm latency 40% so với bản cũ
- Tích hợp mô hình AI vào ứng dụng thực tế qua REST API và gRPC
- Phối hợp với Backend và Data team để thiết kế pipeline CI/CD cho ML (MLflow, Kubeflow)
- Mentor 3 junior engineers về best practices ML/Deep Learning

Machine Learning Engineer | BlueOcean Software | 2020 - 2022
- Phát triển hệ thống Recommendation System cho e-commerce, tăng conversion rate 23%
- Xây dựng pipeline xử lý ngôn ngữ tự nhiên (NLP) cho chatbot hỗ trợ khách hàng
- Thí nghiệm và benchmark các mô hình SOTA: BERT, RoBERTa, T5 cho sentiment analysis
- Tối ưu hóa hyperparameter với Optuna, giảm training time 30%
- Viết unit test, integration test cho ML pipeline, coverage > 90%

DỰ ÁN TIÊU BIỂU
1. Fraud Detection System (TensorFlow, PyTorch, Kubernetes, AWS)
   - Xây dựng ensemble model (XGBoost + Neural Network) detect real-time fraud
   - Xử lý 100k transactions/second với latency < 50ms
   - Deploy với TensorFlow Serving trên Kubernetes cluster

2. Medical Image Classification (Computer Vision, PyTorch, Docker)
   - Fine-tune EfficientNet, ResNet cho phân loại bệnh lý X-quang
   - Đạt AUC 0.96 trên dataset CheXpert
   - Triển khai model lên edge device với TensorRT optimization

3. Vietnamese NLP Chatbot (Transformers, Hugging Face, FastAPI)
   - Fine-tune PhoBERT cho intent classification và entity extraction
   - Xử lý 10k+ requests/day với response time < 200ms

GIÁO DỤC
Thạc sĩ Khoa học Máy tính | ĐH Bách Khoa Hà Nội | 2018 - 2020
Chuyên ngành: Trí tuệ nhân tạo & Machine Learning
Luận văn: "Optimizing Deep Learning Models for Edge Deployment"

Cử nhân Khoa học Máy tính | ĐH Bách Khoa Hà Nội | 2014 - 2018
Xếp loại: Giỏi (GPA: 3.7/4.0)

CHỨNG CHỈ
- AWS Certified Machine Learning - Specialty (2023)
- TensorFlow Developer Certificate (2022)
- Google Cloud Professional ML Engineer (2023)

NGÔN NGỮ
- Tiếng Việt: Native
- Tiếng Anh: IELTS 7.5 (Fluent technical communication)
""",
    },
    {
        "email": "test_otp3@example.com",
        "filename": "cv_data_analyst.txt",
        "title": "Data Analyst / BI Developer",
        "category": "Data",
        "content": """
TRẦN THỊ B
Data Analyst | Business Intelligence Developer
Email: tranthib@email.com | Phone: 0912345678 | LinkedIn: linkedin.com/in/tranthib

TÓM TẮT
Data Analyst với 4 năm kinh nghiệm thu thập, làm sạch, phân tích dữ liệu và xây dựng dashboard báo cáo.
Thành thạo SQL, Python (Pandas, NumPy), Tableau, Power BI, Looker. Có kinh nghiệm làm việc với Big Data (Spark, Hadoop).
Kỹ năng mạnh: Data Visualization, Statistical Analysis, A/B Testing, Business Insights.

KỸ NĂNG CHUYÊN MÔN
- Data Analysis: Pandas, NumPy, SciPy, Statistical Testing, Hypothesis Testing, A/B Testing
- SQL: PostgreSQL, MySQL, BigQuery, Snowflake, Complex Joins, Window Functions, CTEs, Query Optimization
- Visualization: Tableau, Power BI, Looker, Matplotlib, Seaborn, Plotly, Dash/Streamlit
- Big Data: Apache Spark, PySpark, Hadoop, Hive, DataBricks
- ETL/ELT: Airflow, dbt, Fivetran, Custom Python ETL pipelines
- Statistics: Descriptive/Inferential Statistics, Regression, Time Series Analysis, Forecasting
- Tools: Jupyter, Git, Docker, Linux, Excel (Advanced: Pivot, Power Query, VBA)

KINH NGHIỆM LÀM VIỆC

Senior Data Analyst | Innovatech Labs | 2021 - Hiện tại
- Xây dựng và duy trì 50+ dashboard Tableau/Power BI cho C-level và các bộ phận kinh doanh
- Thiết kế ETL pipeline với Airflow + dbt xử lý 500GB+ data hàng ngày từ 20+ nguồn
- Phân tích hành vi người dùng, xây dựng cohort analysis, retention analysis tăng retention 15%
- Thực hiện A/B testing cho các tính năng mới, thống kê ý nghĩa p-value < 0.05
- Tự động hóa báo cáo hàng tuần/tháng, giảm 80% thời gian manual reporting
- Hợp tác với Product, Marketing, Sales để định nghĩa KPI và metric tracking

Data Analyst | TechNova Solutions | 2019 - 2021
- Viết truy vấn SQL phức tạp để khai thác dữ liệu từ Data Warehouse (PostgreSQL, Redshift)
- Xây dựng mô hình dự báo doanh số với Time Series (ARIMA, Prophet), MAPE < 8%
- Phân tích customer segmentation (RFM, K-means clustering) cho chiến lược marketing
- Tạo automated report với Python (Pandas + Jinja2 + Email), gửi tự động cho stakeholders
- Hỗ trợ Data Engineer thiết kế data model (Star Schema, Snowflake Schema)

DỰ ÁN TIÊU BIỂU
1. Executive Dashboard System (Tableau, PostgreSQL, Airflow, dbt)
   - 20+ dashboard real-time cho CEO, CFO, CMO
   - Data freshness < 15 phút, uptime 99.9%

2. Customer Churn Prediction (Python, Scikit-learn, SQL)
   - Xây dựng mô hình phân loại churn với XGBoost, AUC 0.89
   - Tích hợp vào CRM để sales team can thiệp kịp thời

3. Marketing Attribution Model (BigQuery, dbt, Looker)
   - Multi-touch attribution cho ngân sách marketing $2M+/năm
   - Tối ưu phân bổ ngân sách tăng ROAS 25%

GIÁO DỤC
Cử nhân Thống kê & Khoa học Dữ liệu | ĐH Kinh tế Quốc dân | 2015 - 2019
Xếp loại: Xuất sắc (GPA: 3.8/4.0)

CHỨNG CHỈ
- Tableau Desktop Specialist (2022)
- Google Data Analytics Professional Certificate (2021)
- Microsoft Power BI Data Analyst Associate (PL-300) (2023)

NGÔN NGỮ
- Tiếng Việt: Native
- Tiếng Anh: IELTS 7.0 (Business proficiency)
""",
    },
    {
        "email": "test_otp4@example.com",
        "filename": "cv_backend_dev.txt",
        "title": "Backend Developer (Python/Java/Go)",
        "category": "Backend Development",
        "content": """
LÊ VĂN C
Backend Developer | Python / Java / Go
Email: levanc@email.com | Phone: 0923456789 | LinkedIn: linkedin.com/in/levanc
GitHub: github.com/levanc

TÓM TẮT
Backend Developer 5 năm kinh nghiệm thiết kế, phát triển API, microservices, hệ thống high-load.
Thành thạo Python (FastAPI, Django, Flask), Java (Spring Boot), Go (Gin, Echo).
Kinh nghiệm sâu: Database design, Caching, Message Queue, CI/CD, Kubernetes, System Design.

KỸ NĂNG CHUYÊN MÔN
- Languages: Python 3.x, Java 17+, Go 1.20+, TypeScript, SQL
- Frameworks: FastAPI, Django, Flask, Spring Boot, Gin, Echo, gRPC, GraphQL
- Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Cassandra
- Message Queue: RabbitMQ, Kafka, NATS, Redis Streams
- Caching: Redis, Memcached, CDN (Cloudflare, AWS CloudFront)
- Infrastructure: Docker, Kubernetes, Helm, Terraform, AWS (ECS, RDS, S3, Lambda), GCP
- CI/CD: GitLab CI, GitHub Actions, Jenkins, ArgoCD
- Architecture: Microservices, Event-Driven, CQRS, Domain-Driven Design (DDD)
- Testing: pytest, JUnit, Testcontainers, Contract Testing (Pact), Load Testing (k6, Locust)
- Monitoring: Prometheus, Grafana, ELK Stack, Jaeger, OpenTelemetry

KINH NGHIỆM LÀM VIỆC

Senior Backend Engineer | DataVision Solutions | 2021 - Hiện tại
- Thiết kế và phát triển microservices architecture cho hệ thống fintech xử lý 1M+ transactions/day
- Xây dựng API Gateway (Kong), service mesh (Istio), distributed tracing (Jaeger)
- Tối ưu query PostgreSQL, giảm 60% latency cho các endpoint critical
- Triển khai Event-Driven Architecture với Kafka, xử lý eventual consistency
- Mentor team 5 developers, code review, thiết lập coding standard
- Thiết lập CI/CD pipeline zero-downtime deployment với ArgoCD + Helm

Backend Developer (Python/Java) | CloudCore Technology | 2018 - 2021
- Phát triển RESTful API với FastAPI/Spring Boot cho các sản phẩm SaaS
- Thiết kế database schema, migration với Alembic/Liquibase
- Implement authentication/authorization: OAuth2, JWT, RBAC, SSO (Keycloak)
- Xây dựng background job processing với Celery/Redis, Dramatiq
- Integrate third-party APIs: Payment (Stripe, VNPay), Email (SendGrid), SMS (Twilio)
- Viết unit/integration test, đạt coverage > 85%

DỰ ÁN TIÊU BIỂU
1. High-Throughput Payment Gateway (Go, PostgreSQL, Kafka, Kubernetes)
   - Xử lý 10k TPS, latency p99 < 100ms
   - Idempotency, distributed transaction (Saga pattern)
   - PCI-DSS compliance, audit logging

2. Real-time Notification Service (Python, FastAPI, WebSocket, Redis)
   - Push 100k+ concurrent connections
   - Multi-channel: Email, SMS, Push, In-app
   - Horizontal scaling với Redis Pub/Sub

3. E-commerce Order Management (Java, Spring Boot, MySQL, RabbitMQ)
   - Microservices: Order, Inventory, Payment, Shipping
   - Event sourcing cho order state machine
   - Distributed tracing, circuit breaker (Resilience4j)

GIÁO DỤC
Cử nhân Khoa học Máy tính | ĐH Công nghệ Thông tin TP.HCM | 2014 - 2018
Xếp loại: Giỏi

CHỨNG CHỈ
- AWS Certified Solutions Architect - Associate (2022)
- CKAD: Certified Kubernetes Application Developer (2023)
- Oracle Certified Professional Java SE 17 Developer (2021)

NGÔN NGỮ
- Tiếng Việt: Native
- Tiếng Anh: IELTS 7.0 (Technical documentation fluent)
""",
    },
    {
        "email": "test_otp5@example.com",
        "filename": "cv_frontend_dev.txt",
        "title": "Frontend Developer (React/Vue/TypeScript)",
        "category": "Frontend Development",
        "content": """
PHẠM THỊ D
Frontend Developer | React / Vue / TypeScript
Email: phamthid@email.com | Phone: 0934567890 | LinkedIn: linkedin.com/in/phamthid
GitHub: github.com/phamthid | Portfolio: phamthid.dev

TÓM TẮT
Frontend Developer 4 năm kinh nghiệm xây dựng Single Page Applications, Design Systems, Performance Optimization.
Chuyên React/Next.js, Vue/Nuxt, TypeScript. Có kinh nghiệm: State Management, Testing, CI/CD, Accessibility (WCAG).
Đam mê: Clean Code, Component Architecture, Developer Experience, Web Vitals Optimization.

KỸ NĂNG CHUYÊN MÔN
- Core: JavaScript (ES6+), TypeScript, HTML5, CSS3, Sass/Less, Tailwind CSS, CSS Modules
- Frameworks: React 18, Next.js 14, Vue 3, Nuxt 3, SvelteKit
- State Management: Redux Toolkit, Zustand, Jotai, Vuex, Pinia, React Query/TanStack Query
- UI Libraries: Material UI, Ant Design, Chakra UI, Headless UI, Radix UI, Shadcn/UI
- Testing: Jest, Vitest, React Testing Library, Cypress, Playwright, Storybook
- Build Tools: Vite, Webpack, Turbopack, esbuild, Rollup
- Performance: Code Splitting, Lazy Loading, SSR/SSG/ISR, Image Optimization, Bundle Analysis
- Architecture: Component-Driven Development, Atomic Design, Micro-frontends (Module Federation)
- Tools: Git, ESLint, Prettier, Husky, lint-staged, Chrome DevTools, Lighthouse

KINH NGHIỆM LÀM VIỆC

Senior Frontend Engineer | TechNova Solutions | 2021 - Hiện tại
- Lead frontend cho sản phẩm B2B SaaS (React, Next.js, TypeScript), team 6 devs
- Xây dựng Design System component library (Storybook, Chromatic, 50+ components)
- Triển khai Micro-frontends architecture với Module Federation (Webpack 5)
- Tối ưu Core Web Vitals: LCP < 1.5s, FID < 50ms, CLS < 0.1, Lighthouse Score 95+
- Thiết lập CI/CD: GitHub Actions + Vercel/Netlify, Preview Deployments, Visual Regression Testing
- Mentor junior devs, code review, RFC process cho technical decisions

Frontend Developer | Digital Future Lab | 2019 - 2021
- Phát triển dashboard analytics real-time (React, Redux, WebSocket, D3.js/Recharts)
- Migration từ Vue 2 (Options API) → Vue 3 (Composition API) + TypeScript
- Implement Server-Side Rendering (Next.js) cho SEO-critical pages
- Xây dựng reusable component library, documentation với Storybook
- Unit/E2E testing: Jest + RTL (coverage 80%), Cypress cho critical user flows
- Accessibility audit & fix (WCAG 2.1 AA compliance)

DỰ ÁN TIÊU BIỂU
1. Enterprise Design System (React, TypeScript, Storybook, Chromatic, Tailwind)
   - 60+ accessible components, design tokens, theming support
   - Adopted by 5 product teams, 200+ developers
   - Zero-bundle-size impact với tree-shaking

2. Real-time Collaborative Editor (React, Yjs, WebRTC, WebSocket)
   - Google Docs-like collaborative editing
   - Conflict-free replicated data type (CRDT) cho offline support
   - 10k+ concurrent users, sub-100ms sync latency

3. E-commerce PWA (Next.js, React Query, Stripe, Workbox)
   - SSR/ISR cho product pages, SSG cho blog
   - Offline-first với Service Worker, Background Sync
   - Conversion rate tăng 18% sau migration từ SPA

GIÁO DỤC
Cử nhân Khoa học Máy tính | ĐH Sư phạm Kỹ thuật TP.HCM | 2015 - 2019

CHỨNG CHỈ
- Meta Front-End Developer Professional Certificate (2022)
- Google UX Design Professional Certificate (2021)

NGÔN NGỮ
- Tiếng Việt: Native
- Tiếng Anh: IELTS 7.5 (Fluent technical communication)
""",
    },
    {
        "email": "test_otp6@example.com",
        "filename": "cv_devops.txt",
        "title": "DevOps / Cloud Engineer",
        "category": "DevOps / Cloud",
        "content": """
HOÀNG VĂN E
DevOps Engineer | Cloud Engineer | SRE
Email: hoangvane@email.com | Phone: 0945678901 | LinkedIn: linkedin.com/in/hoangvane
GitHub: github.com/hoangvane

TÓM TẮT
DevOps/Cloud Engineer 5 năm kinh nghiệm Infrastructure as Code, CI/CD, Kubernetes, Observability.
Chuyên AWS, GCP, Terraform, Kubernetes, Helm, ArgoCD, Prometheus/Grafana.
Kinh nghiệm: Platform Engineering, GitOps, Security Hardening, Cost Optimization, Disaster Recovery.

KỸ NĂNG CHUYÊN MÔN
- Cloud: AWS (EKS, EC2, RDS, S3, Lambda, CloudFront, IAM, VPC), GCP (GKE, Cloud Run, Cloud SQL), Azure (AKS)
- IaC: Terraform, Terragrunt, Pulumi, Crossplane, AWS CDK
- Kubernetes: EKS/GKE/AKS, Helm, Kustomize, Operators, CRDs, Istio, Linkerd, Cert-Manager, External-DNS
- GitOps: ArgoCD, Flux, Helmfile, Kustomize
- CI/CD: GitLab CI, GitHub Actions, Jenkins, Tekton, Buildkite
- Container: Docker, Podman, BuildKit, Kaniko, Cosign (Signing), Trivy (Scanning)
- Monitoring: Prometheus, Grafana, Alertmanager, Loki, Tempo, Pyroscope, OpenTelemetry
- Logging: ELK/EFK Stack, Loki, Vector, Fluent Bit
- Security: Vault, Sealed Secrets, Kyverno, OPA Gatekeeper, Trivy, Falco, Kube-bench
- Networking: CNI (Cilium, Calico), Service Mesh (Istio), Ingress (NGINX, Traefik), DNS, TLS/mTLS
- Scripting: Bash, Python, Go, Groovy (Jenkins)

KINH NGHIỆM LÀM VIỆC

Senior DevOps Engineer | DataVision Solutions | 2020 - Hiện tại
- Thiết kế và vận hành Kubernetes platform (EKS) cho 50+ microservices, multi-tenant
- Triển khai GitOps workflow với ArgoCD: 200+ applications, progressive delivery (Canary, Blue/Green)
- Xây dựng Internal Developer Platform (Backstage, Crossplane) cho self-service infrastructure
- Infrastructure as Code: Terraform modules (VPC, EKS, RDS, S3, IAM), Terragrunt cho multi-env
- Cost optimization: Right-sizing, Spot Instances, Savings Plans, giảm 35% cloud bill
- Security hardening: CIS Benchmarks, Pod Security Standards, Network Policies, mTLS
- Disaster Recovery: Backup/Restore (Velero), Cross-region replication, RTO < 1h, RPO < 5min

DevOps Engineer | CloudCore Technology | 2017 - 2020
- Migration từ VM-based → Container/Kubernetes (on-prem → AWS EKS)
- Thiết lập CI/CD pipeline cho 30+ repos: Build, Test, Security Scan, Deploy
- Implement Infrastructure as Code với Terraform, quản lý state remote (S3 + DynamoDB)
- Monitoring stack: Prometheus Operator, Grafana, Loki, Tempo (Full observability)
- Log aggregation: EFK Stack → Loki + Promtail (giảm 60% storage cost)
- Incident response: Runbook automation, On-call rotation, Postmortem culture

DỰ ÁN TIÊU BIỂU
1. Multi-Cluster Kubernetes Platform (EKS, ArgoCD, Terraform, Cilium, Istio)
   - 5 clusters (prod, staging, dev, dr, sandbox) across 3 AWS regions
   - Cluster API cho cluster lifecycle management
   - Platform team support 100+ developers

2. GitOps CI/CD Platform (GitHub Actions, ArgoCD, Helm, Kustomize)
   - 500+ deployments/day, zero-downtime
   - Policy-as-code: OPA Gatekeeper, Kyverno
   - Supply chain security: SLSA Level 3, Cosign signing, SBOM generation

3. Observability Stack Migration (Datadog → Prometheus/Grafana/Loki/Tempo)
   - Full stack observability: Metrics, Logs, Traces, Profiles
   - Cost reduction: $50k/month → $8k/month (self-hosted on EKS)
   - SLO/SLI framework, Error Budget alerting

GIÁO DỤC
Cử nhân Hệ thống Thông tin | ĐH Bách Khoa Đà Nẵng | 2013 - 2017

CHỨNG CHỈ
- AWS Certified DevOps Engineer - Professional (2022)
- CKA: Certified Kubernetes Administrator (2021)
- CKS: Certified Kubernetes Security Specialist (2023)
- HashiCorp Certified: Terraform Associate (2022)

NGÔN NGỮ
- Tiếng Việt: Native
- Tiếng Anh: IELTS 7.0 (Technical documentation fluent)
""",
    },
]


def main():
    print("=" * 60)
    print("Creating Sample CVs for IT Career Match")
    print("=" * 60)

    for cv_data in SAMPLE_CVS:
        email = cv_data["email"]
        filename = cv_data["filename"]
        content = cv_data["content"]

        print(f"\n[CV] Processing: {cv_data['title']} ({email})")

        # Extract skills from CV content
        skills = extract_skills(content)
        print(f"   Extracted {len(skills)} skills: {', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}")

        # Get user_id from email
        from database.connection_pool import get_cursor
        with get_cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

        if not user:
            print(f"   ❌ User not found: {email}")
            continue

        user_id = user["user_id"]
        print(f"   User ID: {user_id}")

        # Create CV record (no file path for text-based CV)
        cv_id = create_cv(user_id, filename, "", content, skills)
        print(f"   [OK] CV created: cv_id={cv_id}")

        # Add skills to user profile
        for skill_name in skills:
            skill_id = get_skill_id_by_name(skill_name)
            if skill_id:
                add_student_skill(user_id, skill_id)
        print(f"   [OK] Added {len(skills)} skills to profile")

    print("\n" + "=" * 60)
    print("[OK] All sample CVs created successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()