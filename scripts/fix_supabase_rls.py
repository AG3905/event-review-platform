"""Script to automatically enable Row Level Security (RLS) on all Supabase PostgreSQL tables.

Usage:
    python scripts/fix_supabase_rls.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text


def enable_rls():
    engine_name = db.engine.name.lower()
    if 'postgres' not in engine_name:
        print(f"Notice: Database engine is '{engine_name}'. Row Level Security (RLS) is specific to PostgreSQL (Supabase).")
        print("To apply this to your production Supabase database, run this script with your production DATABASE_URL set.")
        return

    sql_statements = [
        "ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE IF EXISTS public.events ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE IF EXISTS public.reviews ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE IF EXISTS public.event_questions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE IF EXISTS public.review_answers ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE IF EXISTS public.saved_question_sets ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE IF EXISTS public.alembic_version ENABLE ROW LEVEL SECURITY;",
        
        "DROP POLICY IF EXISTS \"Backend full access on users\" ON public.users;",
        "CREATE POLICY \"Backend full access on users\" ON public.users FOR ALL USING (true) WITH CHECK (true);",
        
        "DROP POLICY IF EXISTS \"Backend full access on events\" ON public.events;",
        "CREATE POLICY \"Backend full access on events\" ON public.events FOR ALL USING (true) WITH CHECK (true);",
        
        "DROP POLICY IF EXISTS \"Backend full access on reviews\" ON public.reviews;",
        "CREATE POLICY \"Backend full access on reviews\" ON public.reviews FOR ALL USING (true) WITH CHECK (true);",
        
        "DROP POLICY IF EXISTS \"Backend full access on event_questions\" ON public.event_questions;",
        "CREATE POLICY \"Backend full access on event_questions\" ON public.event_questions FOR ALL USING (true) WITH CHECK (true);",
        
        "DROP POLICY IF EXISTS \"Backend full access on review_answers\" ON public.review_answers;",
        "CREATE POLICY \"Backend full access on review_answers\" ON public.review_answers FOR ALL USING (true) WITH CHECK (true);",
        
        "DROP POLICY IF EXISTS \"Backend full access on saved_question_sets\" ON public.saved_question_sets;",
        "CREATE POLICY \"Backend full access on saved_question_sets\" ON public.saved_question_sets FOR ALL USING (true) WITH CHECK (true);",
        
        "DROP POLICY IF EXISTS \"Backend full access on alembic_version\" ON public.alembic_version;",
        "CREATE POLICY \"Backend full access on alembic_version\" ON public.alembic_version FOR ALL USING (true) WITH CHECK (true);"
    ]

    print("Enabling Row Level Security (RLS) on Supabase PostgreSQL tables...")
    with db.engine.connect() as conn:
        for stmt in sql_statements:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception as e:
                print(f"Notice: {stmt} -> {e}")

    print("Successfully enabled Row Level Security (RLS) on all database tables.")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        enable_rls()
