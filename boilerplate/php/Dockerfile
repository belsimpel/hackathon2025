FROM php:8.2-cli

# Install Composer
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

WORKDIR /app

COPY composer.json /app/composer.json

RUN composer install --no-interaction --no-ansi

COPY . /app

CMD ["php", "-S", "0.0.0.0:8000", "-t", "/app"]
