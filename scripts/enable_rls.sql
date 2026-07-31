-- ==============================================================================
-- SUPABASE ROW LEVEL SECURITY (RLS) FIX SCRIPT
-- Resolves Supabase Security Warning: "RLS Disabled in Public Entity"
-- ==============================================================================

-- 1. Enable RLS on all public tables
ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.event_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.review_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.saved_question_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.alembic_version ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing policies if re-running
DROP POLICY IF EXISTS "Backend full access on users" ON public.users;
DROP POLICY IF EXISTS "Backend full access on events" ON public.events;
DROP POLICY IF EXISTS "Backend full access on reviews" ON public.reviews;
DROP POLICY IF EXISTS "Backend full access on event_questions" ON public.event_questions;
DROP POLICY IF EXISTS "Backend full access on review_answers" ON public.review_answers;
DROP POLICY IF EXISTS "Backend full access on saved_question_sets" ON public.saved_question_sets;
DROP POLICY IF EXISTS "Backend full access on alembic_version" ON public.alembic_version;

-- 3. Create full access policies for backend database connection
CREATE POLICY "Backend full access on users" ON public.users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Backend full access on events" ON public.events FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Backend full access on reviews" ON public.reviews FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Backend full access on event_questions" ON public.event_questions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Backend full access on review_answers" ON public.review_answers FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Backend full access on saved_question_sets" ON public.saved_question_sets FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Backend full access on alembic_version" ON public.alembic_version FOR ALL USING (true) WITH CHECK (true);
