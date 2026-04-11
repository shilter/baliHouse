# NOTES

## What I would add with 4 more hours

- **Leads pagination** — `GET /api/leads` returns all matching rows. For large datasets
  this needs `?page=&per_page=` support. The infrastructure (env vars, SQLAlchemy paginate)
  is already in place on the members endpoint — leads would follow the same pattern.

- **Inline notes editing** — notes can only be updated via PATCH. A quick inline edit
  cell in the table row would remove the need to open a separate form.

- **Toast notifications** — replace `window.confirm` and silent fetch failures with
  visible success/error toasts so the user always knows what happened.


## What I deliberately left out

- **Tests** — explicitly excluded per the spec ("don't spend time on this").

- **Mobile responsiveness** — excluded per the spec.

- **Docker** — the stack is straightforward (Python + Node + Postgres). A
  `docker-compose.yml` would make setup easier on a fresh machine but felt like
  over-engineering for a local take-home test.

- **Rate limiting** — `Flask-Limiter` is already in `requirements.txt`. Wiring it up
  per-endpoint would be the next security step but was out of scope here.

- **Email verification** — `Flask-Mail` is configured in `.env` and `requirements.txt`.
  Sending a confirmation email on register is the natural next step but not required
  by the spec.