# Placeholder for User and DB models.
# In a real SaaS, this would use SQLAlchemy or Prisma Python bindings.

class User:
    def __init__(self, clerk_id, email, credits=250):
        self.clerk_id = clerk_id
        self.email = email
        self.credits = credits

class GeneratedImage:
    def __init__(self, user_id, url, tipo_ensaio):
        self.user_id = user_id
        self.url = url
        self.tipo_ensaio = tipo_ensaio
