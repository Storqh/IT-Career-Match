#!/usr/bin/env python
"""
Comprehensive UI Testing & BA Analysis Script
Acts as both Tester (automated checks) and BA (issue identification)
"""
import re
from app import create_app
from bs4 import BeautifulSoup

app = create_app()

def analyze_html(html, url, role="student"):
    """Analyze HTML for common UI/UX issues"""
    issues = []
    warnings = []
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Check for missing critical elements
    if 'dashboard-layout' in html:
        if not soup.select('.app-sidebar'):
            issues.append(f"[{url}] Missing .app-sidebar in dashboard layout")
        if not soup.select('.app-header'):
            issues.append(f"[{url}] Missing .app-header in dashboard layout")
        if not soup.select('main, .main-content, [role="main"]'):
            warnings.append(f"[{url}] No main content area found")

    # 2. Check chatbot inclusion
    if 'careerChatbot' not in html:
        issues.append(f"[{url}] Chatbot not included")

    # 3. Check for hardcoded colors (should use CSS variables)
    hardcoded_colors = re.findall(r'style="[^"]*#[0-9a-fA-F]{3,8}', html)
    if hardcoded_colors:
        issues.append(f"[{url}] Hardcoded hex colors found: {hardcoded_colors[:3]}")

    # 4. Check for inline styles that should be classes
    inline_styles = re.findall(r'style="[^"]{50,}"', html)
    if len(inline_styles) > 5:
        warnings.append(f"[{url}] Many inline styles ({len(inline_styles)}) - consider CSS classes")

    # 5. Check accessibility - images without alt
    imgs = soup.find_all('img')
    for img in imgs:
        if not img.get('alt') and not img.get('aria-hidden'):
            warnings.append(f"[{url}] Image missing alt: {img.get('src', 'unknown')}")

    # 6. Check form labels
    inputs = soup.find_all(['input', 'select', 'textarea'])
    for inp in inputs:
        if inp.get('type') not in ['hidden', 'submit', 'button', 'checkbox', 'radio']:
            input_id = inp.get('id')
            if input_id:
                label = soup.find('label', attrs={'for': input_id})
                if not label:
                    warnings.append(f"[{url}] Input #{input_id} missing associated label")

    # 7. Check for duplicate IDs
    all_ids = [el.get('id') for el in soup.find_all(id=True)]
    dup_ids = [id for id in set(all_ids) if all_ids.count(id) > 1]
    if dup_ids:
        issues.append(f"[{url}] Duplicate IDs: {dup_ids}")

    # 8. Check Bootstrap 5.3 compatibility
    if 'class="form-group"' in html:
        warnings.append(f"[{url}] Uses deprecated 'form-group' class (Bootstrap 4)")
    if 'class="input-group-prepend"' in html or 'class="input-group-append"' in html:
        warnings.append(f"[{url}] Uses deprecated input-group-prepend/append")

    # 9. Check for missing CSRF tokens in forms
    forms = soup.find_all('form', method=re.compile(r'POST', re.I))
    for form in forms:
        csrf = form.find('input', attrs={'name': re.compile(r'csrf|_token', re.I)})
        if not csrf and '/api/' not in (form.get('action') or ''):
            warnings.append(f"[{url}] POST form may be missing CSRF token")

    # 10. Check responsive meta tag
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport:
        issues.append(f"[{url}] Missing viewport meta tag")

    # 11. Check for console errors in inline scripts
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'console.error' in script.string:
            warnings.append(f"[{url}] console.error in inline script")

    # 12. Check empty states for data tables/lists
    if 'dashboard' in url or 'admin' in url:
        empty_states = soup.find_all(class_=re.compile(r'empty|no-data|no-results'))
        if not empty_states:
            # Check if there are tables that might be empty
            tables = soup.find_all('table')
            for table in tables:
                tbody = table.find('tbody')
                if tbody and not tbody.find('tr'):
                    warnings.append(f"[{url}] Empty table without empty state message")

    # 13. Check sidebar active state
    if 'app-sidebar' in html:
        active_links = soup.select('.app-sidebar .nav-link.active, .app-sidebar .sidebar-item.active')
        if not active_links:
            warnings.append(f"[{url}] No active state in sidebar navigation")

    # 14. Check for proper heading hierarchy
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    prev_level = 0
    for h in headings:
        level = int(h.name[1])
        if level - prev_level > 1:
            warnings.append(f"[{url}] Heading hierarchy skip: h{prev_level} -> h{level}")
        prev_level = level

    # 15. Check for pro-ui CSS variable usage
    css_var_usage = len(re.findall(r'var\(--icm-', html))
    if css_var_usage == 0 and 'dashboard' in url:
        warnings.append(f"[{url}] No pro-ui CSS variables used (--icm-*)")

    return issues, warnings


def run_comprehensive_test():
    """Run comprehensive tests across all pages"""
    with app.app_context():
        with app.test_client() as client:
            # Public pages
            public_pages = [
                ('/', 'home'),
                ('/jobs/', 'jobs_list'),
                ('/jobs/13', 'job_detail'),
                ('/login', 'login'),
                ('/register', 'register'),
                ('/forgot-password', 'forgot_password'),
            ]

            # Student pages (need session)
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['user_role'] = 'student'
                sess['user_email'] = 'test@test.com'

            student_pages = [
                ('/profile/dashboard', 'dashboard'),
                ('/profile/edit', 'edit_profile'),
                ('/cv/my-cvs', 'my_cvs'),
                ('/cv/upload', 'upload_cv'),
                ('/cv/recommendations', 'recommendations'),
                ('/jobs/my-applications', 'my_applications'),
                ('/jobs/my-favourites', 'my_favourites'),
                ('/cv/parse-text', 'parse_text'),
                ('/cv/gap-analysis/13', 'gap_analysis'),
            ]

            # Admin pages (need admin session)
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['user_role'] = 'admin'
                sess['user_email'] = 'admin@test.com'

            admin_pages = [
                ('/jobs/admin', 'admin_jobs'),
                ('/admin/', 'admin_dashboard'),
                ('/admin/users', 'admin_users'),
                ('/admin/applications', 'admin_applications'),
                ('/admin/analytics', 'admin_analytics'),
                ('/admin/settings', 'admin_settings'),
            ]

            all_pages = [
                *[(url, name, 'public') for url, name in public_pages],
                *[(url, name, 'student') for url, name in student_pages],
                *[(url, name, 'admin') for url, name in admin_pages],
            ]

            all_issues = []
            all_warnings = []
            passed = 0
            failed = 0

            print("=" * 80)
            print("COMPREHENSIVE UI TEST & BA ANALYSIS REPORT")
            print("=" * 80)

            for url, name, role in all_pages:
                try:
                    response = client.get(url)
                    html = response.get_data(as_text=True)

                    issues, warnings = analyze_html(html, url, role)

                    if response.status_code >= 400:
                        issues.append(f"[{url}] HTTP {response.status_code}")

                    if issues:
                        failed += 1
                        print(f"\n[FAIL] {name} ({url})")
                        for issue in issues:
                            print(f"  [ISSUE] {issue}")
                        all_issues.extend(issues)
                    else:
                        passed += 1
                        print(f"[PASS] {name} ({url})")

                    if warnings:
                        for warning in warnings:
                            print(f"  [WARN] {warning}")
                        all_warnings.extend(warnings)

                except Exception as e:
                    failed += 1
                    print(f"\n[ERROR] {name} ({url}) - {e}")
                    all_issues.append(f"[{url}] Exception: {e}")

            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Pages tested: {len(all_pages)}")
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            print(f"Total Issues: {len(all_issues)}")
            print(f"Total Warnings: {len(all_warnings)}")

            if all_issues:
                print("\n[CRITICAL ISSUES - Must Fix]:")
                for i, issue in enumerate(all_issues, 1):
                    print(f"  {i}. {issue}")

            if all_warnings:
                print("\n[WARNINGS - Should Fix]:")
                for i, warning in enumerate(all_warnings, 1):
                    print(f"  {i}. {warning}")

            # BA Recommendations
            print("\n" + "=" * 80)
            print("BA RECOMMENDATIONS FOR DEV TEAM")
            print("=" * 80)

            recommendations = [
                "1. Run visual regression tests at breakpoints: 1920px, 1440px, 1366px, 768px, 390px, 375px",
                "2. Test sidebar collapse/expand and mobile drawer on real devices",
                "3. Verify chatbot z-index (99999) doesn't conflict with modals/dropdowns",
                "4. Test dark mode toggle across all pages",
                "5. Verify keyboard navigation (Tab order, focus indicators)",
                "6. Test screen reader compatibility (NVDA/VoiceOver)",
                "7. Check color contrast ratios meet WCAG AA",
                "8. Test form validation messages display correctly",
                "9. Verify toast notifications appear and dismiss properly",
                "10. Test all interactive elements: dropdowns, modals, accordions, tabs",
            ]
            for rec in recommendations:
                print(f"  {rec}")

            return failed == 0


if __name__ == '__main__':
    success = run_comprehensive_test()
    exit(0 if success else 1)