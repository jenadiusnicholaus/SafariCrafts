# Reviews App - API Architecture

## ✅ **DRF API-First Architecture**

This reviews app uses **DRF serializers and APIViews** for all operations because:

### 🎯 **Project Architecture Consistency**
- SafariCrafts uses **API-first architecture** with DRF
- All other apps (authentication, catalog, artists) use DRF serializers
- Maintains consistent codebase patterns across the entire project

### ⚡ **Technical Benefits**
- **JWT Authentication** - Token-based, not session-based
- **JSON API responses** - Modern frontend consumption
- **OpenAPI documentation** - Auto-generated with drf-spectacular
- **Flexible clients** - Mobile apps, SPAs, external integrations
- **No Django forms needed** - Pure API approach

### 🚀 **API Endpoints**

#### **Core Review Operations:**
- `GET /api/v1/reviews/api/` - List reviews with filtering
- `POST /api/v1/reviews/api/artwork/{id}/create/` - Create review
- `GET /api/v1/reviews/api/{id}/` - Review details
- `PATCH /api/v1/reviews/api/{id}/update/` - Update own review
- `DELETE /api/v1/reviews/api/{id}/delete/` - Delete own review

#### **Interactive Features:**
- `POST /api/v1/reviews/api/{id}/helpfulness/` - Vote helpful/not helpful
- `POST /api/v1/reviews/api/{id}/respond/` - Respond to review
- `POST /api/v1/reviews/api/{id}/report/` - Report inappropriate content

#### **Statistics & User Reviews:**
- `GET /api/v1/reviews/api/artwork/{id}/stats/` - Review statistics
- `GET /api/v1/reviews/api/user/` - My reviews
- `GET /api/v1/reviews/api/user/{id}/` - User's public reviews

#### **Admin/Moderation:**
- `PATCH /api/v1/reviews/api/{id}/moderate/` - Moderate review
- `GET /api/v1/reviews/api/admin/pending/` - Pending reviews
- `GET /api/v1/reviews/api/admin/reported/` - Reported reviews

### 🔧 **Advanced Features**
- **Pagination** - Built-in DRF pagination
- **Filtering** - By rating, artwork, verified purchases
- **Search** - Full-text search in title/comment
- **Ordering** - By date, rating, helpfulness
- **Permissions** - Fine-grained access control
- **Validation** - Comprehensive data validation

### 📚 **API Documentation**
Visit `/api/docs/` for interactive Swagger documentation.

### � **Frontend Integration**
Use these APIs with:
- **React/Vue.js** frontends
- **Mobile apps** (iOS/Android)
- **External integrations**
- **Admin dashboards**

No Django templates or forms needed - pure API approach! 🎯
