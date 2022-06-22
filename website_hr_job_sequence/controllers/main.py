# -*- coding: utf-8 -*-

# import imp 
from odoo import http, _
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment


class WebsiteHrRecruitment(http.Controller):

    @http.route([
            '/jobs',
            '/jobs/country/<model("res.country"):country>',
            '/jobs/department/<model("hr.department"):department>',
            '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
            '/jobs/office/<int:office_id>',
            '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
            '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
            '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
        ], type='http', auth="public", website=True, sitemap=WebsiteHrRecruitment.sitemap_jobs)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Country = env['res.country']
        Jobs = env['hr.job']

        # List jobs available to current UID
        domain = request.website.website_domain()
        job_ids = Jobs.search(domain, order="sequence_number asc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)

        # Default search by user country
        if not (country or department or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter job / office for country
        if country and not kwargs.get('all_countries'):
            jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
            offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        else:
            offices = set(j.address_id for j in jobs if j.address_id)

        # Deduce departments and countries offices of those jobs
        departments = set(j.department_id for j in jobs if j.department_id)
        countries = set(o.country_id for o in offices if o.country_id)

        if department:
            jobs = [j for j in jobs if j.department_id and j.department_id.id == department.id]
        if office_id and office_id in [x.id for x in offices]:
            jobs = [j for j in jobs if j.address_id and j.address_id.id == office_id]
        else:
            office_id = False

        # Render page
        return request.render("website_hr_recruitment.index", {
            'jobs': jobs,
            'countries': countries,
            'departments': departments,
            'offices': offices,
            'country_id': country,
            'department_id': department,
            'office_id': office_id,
        })