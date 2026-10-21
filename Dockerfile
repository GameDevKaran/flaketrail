FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOST=0.0.0.0 PORT=8786
ARG SOURCE_COMMIT=unknown
ENV SOURCE_COMMIT=$SOURCE_COMMIT
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
WORKDIR /app
RUN groupadd --gid 10001 flaketrail && useradd --uid 10001 --gid 10001 --no-create-home flaketrail
COPY flaketrail ./flaketrail
COPY web ./web
COPY LICENSE ./LICENSE
USER 10001:10001
EXPOSE 8786
CMD ["python", "-m", "flaketrail.web"]
