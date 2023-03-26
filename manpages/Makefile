update:
	for mdoc in *.mdoc; do \
		mandoc -Tman $$mdoc | sed '/TH/s,"NetBSD [^"]*","NiH",' > $$mdoc.man; \
		mandoc -Thtml -Oman="%N.html",style=../nih-man.css $$mdoc | sed -e 's,href="re_format.html",href="http://pubs.opengroup.org/onlinepubs/9699919799/functions/re_format.html",' -e 's/<td class="foot-os">NetBSD [^<]*/<td class="foot-os">NiH/' > $$mdoc.html; \
		base=$${mdoc%%.mdoc}; \
		diff -qI NiH $$mdoc.man $$base.man || mv $$mdoc.man $$base.man; \
		diff -qI NiH $$mdoc.html $$base.html || mv $$mdoc.html $$base.html; \
		rm -f $$mdoc.man $$mdoc.html; \
	done
