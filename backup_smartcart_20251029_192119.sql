--
-- PostgreSQL database dump
--

\restrict 1jmgXxsFlvg1ptZJzt5cnzaykO9wiJhoV1d4lziBQ9CvpDZv6w3gS1mXxUBoMtU

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: budgets; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.budgets (
    id integer NOT NULL,
    household_id integer,
    month character varying NOT NULL,
    amount double precision NOT NULL,
    spent double precision
);


ALTER TABLE public.budgets OWNER TO smartcart;

--
-- Name: budgets_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.budgets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.budgets_id_seq OWNER TO smartcart;

--
-- Name: budgets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.budgets_id_seq OWNED BY public.budgets.id;


--
-- Name: household_settings; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.household_settings (
    id integer NOT NULL,
    household_id integer,
    pricing_enabled boolean,
    zip_code character varying,
    latitude double precision,
    longitude double precision,
    radius_miles double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.household_settings OWNER TO smartcart;

--
-- Name: household_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.household_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.household_settings_id_seq OWNER TO smartcart;

--
-- Name: household_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.household_settings_id_seq OWNED BY public.household_settings.id;


--
-- Name: households; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.households (
    id integer NOT NULL,
    name character varying NOT NULL,
    created_at timestamp without time zone,
    budget double precision
);


ALTER TABLE public.households OWNER TO smartcart;

--
-- Name: households_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.households_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.households_id_seq OWNER TO smartcart;

--
-- Name: households_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.households_id_seq OWNED BY public.households.id;


--
-- Name: members; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.members (
    id integer NOT NULL,
    household_id integer,
    name character varying NOT NULL,
    role character varying,
    age integer,
    allergies character varying,
    dislikes character varying,
    likes character varying,
    favorite_recipes character varying,
    dietary_pref character varying
);


ALTER TABLE public.members OWNER TO smartcart;

--
-- Name: members_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.members_id_seq OWNER TO smartcart;

--
-- Name: members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.members_id_seq OWNED BY public.members.id;


--
-- Name: pantry_items; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.pantry_items (
    id integer NOT NULL,
    household_id integer,
    name character varying NOT NULL,
    quantity double precision,
    unit character varying,
    expires_at timestamp without time zone,
    staple boolean
);


ALTER TABLE public.pantry_items OWNER TO smartcart;

--
-- Name: pantry_items_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.pantry_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pantry_items_id_seq OWNER TO smartcart;

--
-- Name: pantry_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.pantry_items_id_seq OWNED BY public.pantry_items.id;


--
-- Name: saved_recipe_ingredients; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.saved_recipe_ingredients (
    id integer NOT NULL,
    recipe_id integer,
    name character varying NOT NULL
);


ALTER TABLE public.saved_recipe_ingredients OWNER TO smartcart;

--
-- Name: saved_recipe_ingredients_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.saved_recipe_ingredients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.saved_recipe_ingredients_id_seq OWNER TO smartcart;

--
-- Name: saved_recipe_ingredients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.saved_recipe_ingredients_id_seq OWNED BY public.saved_recipe_ingredients.id;


--
-- Name: saved_recipes; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.saved_recipes (
    id integer NOT NULL,
    household_id integer,
    title character varying NOT NULL,
    url character varying,
    servings integer,
    created_at timestamp without time zone
);


ALTER TABLE public.saved_recipes OWNER TO smartcart;

--
-- Name: saved_recipes_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.saved_recipes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.saved_recipes_id_seq OWNER TO smartcart;

--
-- Name: saved_recipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.saved_recipes_id_seq OWNED BY public.saved_recipes.id;


--
-- Name: shopping_list_items; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.shopping_list_items (
    id integer NOT NULL,
    list_id integer,
    name character varying NOT NULL,
    quantity double precision,
    unit character varying,
    notes character varying,
    shopped boolean
);


ALTER TABLE public.shopping_list_items OWNER TO smartcart;

--
-- Name: shopping_list_items_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.shopping_list_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.shopping_list_items_id_seq OWNER TO smartcart;

--
-- Name: shopping_list_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.shopping_list_items_id_seq OWNED BY public.shopping_list_items.id;


--
-- Name: shopping_lists; Type: TABLE; Schema: public; Owner: smartcart
--

CREATE TABLE public.shopping_lists (
    id integer NOT NULL,
    household_id integer,
    name character varying,
    created_at timestamp without time zone,
    completed_at timestamp without time zone
);


ALTER TABLE public.shopping_lists OWNER TO smartcart;

--
-- Name: shopping_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: smartcart
--

CREATE SEQUENCE public.shopping_lists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.shopping_lists_id_seq OWNER TO smartcart;

--
-- Name: shopping_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartcart
--

ALTER SEQUENCE public.shopping_lists_id_seq OWNED BY public.shopping_lists.id;


--
-- Name: budgets id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.budgets ALTER COLUMN id SET DEFAULT nextval('public.budgets_id_seq'::regclass);


--
-- Name: household_settings id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.household_settings ALTER COLUMN id SET DEFAULT nextval('public.household_settings_id_seq'::regclass);


--
-- Name: households id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.households ALTER COLUMN id SET DEFAULT nextval('public.households_id_seq'::regclass);


--
-- Name: members id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.members ALTER COLUMN id SET DEFAULT nextval('public.members_id_seq'::regclass);


--
-- Name: pantry_items id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.pantry_items ALTER COLUMN id SET DEFAULT nextval('public.pantry_items_id_seq'::regclass);


--
-- Name: saved_recipe_ingredients id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.saved_recipe_ingredients ALTER COLUMN id SET DEFAULT nextval('public.saved_recipe_ingredients_id_seq'::regclass);


--
-- Name: saved_recipes id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.saved_recipes ALTER COLUMN id SET DEFAULT nextval('public.saved_recipes_id_seq'::regclass);


--
-- Name: shopping_list_items id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.shopping_list_items ALTER COLUMN id SET DEFAULT nextval('public.shopping_list_items_id_seq'::regclass);


--
-- Name: shopping_lists id; Type: DEFAULT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.shopping_lists ALTER COLUMN id SET DEFAULT nextval('public.shopping_lists_id_seq'::regclass);


--
-- Data for Name: budgets; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.budgets (id, household_id, month, amount, spent) FROM stdin;
\.


--
-- Data for Name: household_settings; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.household_settings (id, household_id, pricing_enabled, zip_code, latitude, longitude, radius_miles, created_at, updated_at) FROM stdin;
1	1	t	89503	\N	\N	10	2025-10-28 03:40:20.095577	2025-10-28 03:40:20.095589
\.


--
-- Data for Name: households; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.households (id, name, created_at, budget) FROM stdin;
1	Holden	2025-10-28 02:55:52.582019	750
\.


--
-- Data for Name: members; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.members (id, household_id, name, role, age, allergies, dislikes, likes, favorite_recipes, dietary_pref) FROM stdin;
4	1	Judah	child	12	\N	spicy food, pineapple	pizza, cheese, mac and cheese, 	\N	\N
3	1	Flynn	child	20	gluten	vegetables	candy, cheese, pizza, cereal	\N	\N
2	1	Jeanette	adult	53	peanuts	american	british	\N	\N
1	1	Eric	adult	49	fish, mushrooms	cheese	garlic, potatoes, peanut butter	\N	\N
\.


--
-- Data for Name: pantry_items; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.pantry_items (id, household_id, name, quantity, unit, expires_at, staple) FROM stdin;
\.


--
-- Data for Name: saved_recipe_ingredients; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.saved_recipe_ingredients (id, recipe_id, name) FROM stdin;
7	2	1 cup warm water (110 degrees F/45 degrees C)
8	2	2 tablespoons white sugar
9	2	1 (.25 ounce) package bread machine yeast
10	2	0.25 cup vegetable oil
11	2	3 cups bread flour
12	2	1 teaspoon salt
13	3	2 lbs ground beef
14	3	1  medium sweet onion chopped
15	3	2 cloves garlic minced
16	3	3 tablespoons chili powder
17	3	2 teaspoons ground cumin
18	3	1 teaspoon smoked paprika
19	3	½ teaspoon onion powder
20	3	½ teaspoon dried oregano
21	3	1 tablespoon brown sugar
22	3	1 cup low sodium beef broth
23	3	2 tablespoons tomato paste
24	3	2  14.5 ounce can diced tomatoes (do not drain)
25	3	1  15 ounce can kidney beans or pinto beans drained and rinsed
26	3	1  7 ounce can diced green chiles drained
27	3	1  chipotle pepper in adobo sauce finely chopped
28	3	1 tablespoon adobo sauce from the can of chipotle peppers
29	3	salt and pepper to taste
30	4	2 pounds lean ground beef
31	4	1 onion (diced)
32	4	1 jalapeño (seeded and finely diced)
33	4	4 cloves garlic (minced)
34	4	2 ½ tablespoons chili powder (divided, or to taste)
35	4	1 teaspoon cumin
36	4	1 green bell pepper (seeded and diced)
37	4	14.5 ounces crushed tomatoes (1 can)
38	4	19 ounces canned red kidney beans (drained and rinsed)
39	4	14.5 ounces canned diced tomatoes (with juices)
40	4	1 ½ cups beef broth
41	4	1 cup beer
42	4	1 tablespoon tomato paste
43	4	1 tablespoon brown sugar (optional)
44	4	salt and black pepper (to taste)
\.


--
-- Data for Name: saved_recipes; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.saved_recipes (id, household_id, title, url, servings, created_at) FROM stdin;
2	1	Best Bread Machine Bread	https://www.allrecipes.com/recipe/17215/best-bread-machine-bread/	12	2025-10-28 03:10:00.303269
3	1	Best Darn Chili Recipe | Small Town Woman	https://www.smalltownwoman.com/best-chili-recipe/	\N	2025-10-28 03:16:20.841168
4	1	The Best Chili Recipe	https://www.spendwithpennies.com/the-best-chili-recipe/	8	2025-10-28 03:48:22.302659
\.


--
-- Data for Name: shopping_list_items; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.shopping_list_items (id, list_id, name, quantity, unit, notes, shopped) FROM stdin;
1	1	warm water (110 degrees F/45 degrees C)	1	cup	\N	f
2	1	tablespoons white sugar	2	unit	\N	f
3	1	(.25 ounce) package bread machine yeast	1	unit	\N	f
4	1	vegetable oil	0.25	cup	\N	f
5	1	cups bread flour	3	unit	\N	f
6	1	teaspoon salt	1	unit	\N	f
8	2	onion (diced)	1	unit	\N	f
9	2	jalapeño (seeded and finely diced)	1	unit	\N	f
10	2	cloves garlic (minced)	4	unit	\N	f
11	2	½ tablespoons chili powder (divided, or to taste)	2	unit	\N	f
12	2	teaspoon cumin	1	unit	\N	f
13	2	green bell pepper (seeded and diced)	1	unit	\N	f
14	2	ounces crushed tomatoes (1 can)	14.5	unit	\N	f
15	2	ounces canned red kidney beans (drained and rinsed)	19	unit	\N	f
16	2	ounces canned diced tomatoes (with juices)	14.5	unit	\N	f
17	2	½ cups beef broth	1	unit	\N	f
18	2	beer	1	cup	\N	f
19	2	tablespoon tomato paste	1	unit	\N	f
20	2	tablespoon brown sugar (optional)	1	unit	\N	f
21	2	salt and black pepper (to taste)	1	unit	\N	f
7	2	pounds lean ground beef	2	unit	{"selected_offer": {"store": "Safeway", "price": 3.99, "status": "chosen"}}	f
\.


--
-- Data for Name: shopping_lists; Type: TABLE DATA; Schema: public; Owner: smartcart
--

COPY public.shopping_lists (id, household_id, name, created_at, completed_at) FROM stdin;
1	1	Recipe: Best Bread Machine Bread	2025-10-28 03:10:04.448729	\N
2	1	Recipe: The Best Chili Recipe	2025-10-28 03:48:27.484524	\N
\.


--
-- Name: budgets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.budgets_id_seq', 1, false);


--
-- Name: household_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.household_settings_id_seq', 1, true);


--
-- Name: households_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.households_id_seq', 1, true);


--
-- Name: members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.members_id_seq', 4, true);


--
-- Name: pantry_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.pantry_items_id_seq', 1, false);


--
-- Name: saved_recipe_ingredients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.saved_recipe_ingredients_id_seq', 44, true);


--
-- Name: saved_recipes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.saved_recipes_id_seq', 4, true);


--
-- Name: shopping_list_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.shopping_list_items_id_seq', 21, true);


--
-- Name: shopping_lists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: smartcart
--

SELECT pg_catalog.setval('public.shopping_lists_id_seq', 2, true);


--
-- Name: budgets budgets_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_pkey PRIMARY KEY (id);


--
-- Name: household_settings household_settings_household_id_key; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.household_settings
    ADD CONSTRAINT household_settings_household_id_key UNIQUE (household_id);


--
-- Name: household_settings household_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.household_settings
    ADD CONSTRAINT household_settings_pkey PRIMARY KEY (id);


--
-- Name: households households_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.households
    ADD CONSTRAINT households_pkey PRIMARY KEY (id);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (id);


--
-- Name: pantry_items pantry_items_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.pantry_items
    ADD CONSTRAINT pantry_items_pkey PRIMARY KEY (id);


--
-- Name: saved_recipe_ingredients saved_recipe_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.saved_recipe_ingredients
    ADD CONSTRAINT saved_recipe_ingredients_pkey PRIMARY KEY (id);


--
-- Name: saved_recipes saved_recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.saved_recipes
    ADD CONSTRAINT saved_recipes_pkey PRIMARY KEY (id);


--
-- Name: shopping_list_items shopping_list_items_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.shopping_list_items
    ADD CONSTRAINT shopping_list_items_pkey PRIMARY KEY (id);


--
-- Name: shopping_lists shopping_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.shopping_lists
    ADD CONSTRAINT shopping_lists_pkey PRIMARY KEY (id);


--
-- Name: ix_budgets_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_budgets_id ON public.budgets USING btree (id);


--
-- Name: ix_household_settings_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_household_settings_id ON public.household_settings USING btree (id);


--
-- Name: ix_households_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_households_id ON public.households USING btree (id);


--
-- Name: ix_members_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_members_id ON public.members USING btree (id);


--
-- Name: ix_pantry_items_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_pantry_items_id ON public.pantry_items USING btree (id);


--
-- Name: ix_saved_recipe_ingredients_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_saved_recipe_ingredients_id ON public.saved_recipe_ingredients USING btree (id);


--
-- Name: ix_saved_recipes_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_saved_recipes_id ON public.saved_recipes USING btree (id);


--
-- Name: ix_shopping_list_items_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_shopping_list_items_id ON public.shopping_list_items USING btree (id);


--
-- Name: ix_shopping_lists_id; Type: INDEX; Schema: public; Owner: smartcart
--

CREATE INDEX ix_shopping_lists_id ON public.shopping_lists USING btree (id);


--
-- Name: budgets budgets_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id);


--
-- Name: household_settings household_settings_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.household_settings
    ADD CONSTRAINT household_settings_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id);


--
-- Name: members members_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id);


--
-- Name: pantry_items pantry_items_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.pantry_items
    ADD CONSTRAINT pantry_items_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id);


--
-- Name: saved_recipe_ingredients saved_recipe_ingredients_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.saved_recipe_ingredients
    ADD CONSTRAINT saved_recipe_ingredients_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.saved_recipes(id);


--
-- Name: saved_recipes saved_recipes_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.saved_recipes
    ADD CONSTRAINT saved_recipes_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id);


--
-- Name: shopping_list_items shopping_list_items_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.shopping_list_items
    ADD CONSTRAINT shopping_list_items_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.shopping_lists(id);


--
-- Name: shopping_lists shopping_lists_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartcart
--

ALTER TABLE ONLY public.shopping_lists
    ADD CONSTRAINT shopping_lists_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 1jmgXxsFlvg1ptZJzt5cnzaykO9wiJhoV1d4lziBQ9CvpDZv6w3gS1mXxUBoMtU

