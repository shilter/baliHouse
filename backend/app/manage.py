import os
import click
from app.app import create_app
from app.models import db  # noqa: F401 — import semua model agar Alembic mendeteksi tabel

env_name = os.getenv("FLASK_ENV", "development")
app = create_app(env_name)


# ─── CLI: seed-admin ───────────────────────────────────────────────────────────

@app.cli.command('seed-admin')
@click.option('--email',    default=None, help='Email admin (default: SEED_ADMIN_EMAIL env atau admin@admin.com)')
@click.option('--password', default=None, help='Password admin (default: SEED_ADMIN_PASSWORD env atau admin123)')
def cmd_seed_admin(email, password):
    """Buat akun admin pertama (superuser)."""
    if email:
        os.environ['SEED_ADMIN_EMAIL'] = email
    if password:
        os.environ['SEED_ADMIN_PASSWORD'] = password

    from app.seeds.admin_seeder import seed_admin
    click.echo('>>> Menjalankan admin seeder...')
    seed_admin()


# ─── CLI: seed-roles ───────────────────────────────────────────────────────────

@app.cli.command('seed-roles')
def cmd_seed_roles():
    """Seed roles default (customer, agent, villager, admin)."""
    from app.seeds.roles_seeder import seed_roles
    click.echo('>>> Menjalankan roles seeder...')
    seed_roles()


# ─── CLI: seed-menus ───────────────────────────────────────────────────────────

@app.cli.command('seed-menus')
def cmd_seed_menus():
    """Seed menus default untuk semua tipe user."""
    from app.seeds.menus_seeder import seed_menus
    click.echo('>>> Menjalankan menus seeder...')
    seed_menus()


# ─── CLI: seed-all ─────────────────────────────────────────────────────────────

@app.cli.command('seed-all')
def cmd_seed_all():
    """Jalankan semua seeder sekaligus (admin + roles + menus)."""
    from app.seeds.admin_seeder import seed_admin
    from app.seeds.roles_seeder import seed_roles
    from app.seeds.menus_seeder import seed_menus

    click.echo('>>> [1/3] Admin seeder...')
    seed_admin()
    click.echo('>>> [2/3] Roles seeder...')
    seed_roles()
    click.echo('>>> [3/3] Menus seeder...')
    seed_menus()
    click.echo('>>> Semua seeder selesai!')


# ─── CLI: reminder-email ───────────────────────────────────────────────────────

@app.cli.command('reminder-email')
def cmd_reminder_email():
    """Jalankan job reminder email verifikasi secara manual (untuk testing)."""
    from app.task.task_scheduler import _run_reminder_job
    click.echo('>>> Menjalankan reminder email job...')
    total = _run_reminder_job(app)
    click.echo(f'>>> Selesai: {total} email dikirim.')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 1026)), threaded=True)
