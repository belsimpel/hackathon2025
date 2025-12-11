<?php

namespace App\Controllers;

use App\Services\CheckoutService;

class CheckoutController
{
    private CheckoutService $service;

    public function __construct()
    {
        $this->service = new CheckoutService();
    }

    public function process(): void
    {
        echo json_encode([
            'message' => 'Checkout endpoint (not implemented)',
        ]);
    }
}
