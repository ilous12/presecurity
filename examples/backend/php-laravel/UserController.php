<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class UserController extends Controller
{
    public function show(Request $request)
    {
        $id = $request->query('id');
        // Intentional fixture: request parameter is concatenated into SQL.
        return DB::select("select * from users where id = " . $id);
    }
}
